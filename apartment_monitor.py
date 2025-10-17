#!/usr/bin/env python3
"""
Apartment Availability Monitor
Monitors https://www.windsorcommunities.com/properties/windsor-winchester/floorplans/ for apartment availability changes
Checks every 20 seconds and notifies when changes are detected
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
import sys
import json
import re
import os
import requests
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")


class ApartmentMonitor:
    def __init__(self, url: str, check_interval: int = 20, headless: bool = True, 
                 wechat_token: Optional[str] = None, wechat_method: str = 'pushplus',
                 notify_floor_plans: Optional[List[str]] = None,
                 notify_min_bedrooms: Optional[int] = None,
                 email_to: Optional[List[str]] = None, email_from: Optional[str] = None,
                 smtp_server: Optional[str] = None, smtp_port: int = 587,
                 smtp_password: Optional[str] = None):
        """
        Initialize the apartment monitor
        
        Args:
            url: The URL to monitor
            check_interval: Time in seconds between checks
            headless: Whether to run browser in headless mode
            wechat_token: Token for WeChat notifications (optional)
            wechat_method: Method for WeChat notifications ('pushplus', 'serverchan', or 'work')
            notify_floor_plans: List of floor plans to notify about (e.g. ['A', 'B']). 
                              If None, do not filter by plan letters.
            notify_min_bedrooms: If set, only notify for units with this many bedrooms or more.
            email_to: List of email addresses to send notifications to (or single string)
            email_from: Email address to send from
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_password: SMTP password
        """
        self.url = url
        self.check_interval = check_interval
        self.headless = headless
        self.previous_units = {}
        self.wechat_token = wechat_token
        self.wechat_method = wechat_method
        self.notify_floor_plans = [p.upper() for p in notify_floor_plans] if notify_floor_plans else None
        self.notify_min_bedrooms = notify_min_bedrooms
        
        # Handle email_to as either string or list
        if isinstance(email_to, str):
            self.email_to = [email_to]
        elif isinstance(email_to, list):
            self.email_to = email_to
        else:
            self.email_to = None
            
        self.email_from = email_from
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_password = smtp_password
        self.driver = None
        self.floor_plans = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
                           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v']
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            print("❌ Cannot initialize driver: Selenium is not installed")
            return False
        
        try:
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            # Use an isolated user data dir to avoid conflicts in shared envs
            tmp_profile = os.path.join('/tmp', f'selenium-profile-{os.getpid()}')
            try:
                os.makedirs(tmp_profile, exist_ok=True)
                options.add_argument(f'--user-data-dir={tmp_profile}')
            except Exception:
                pass
            
            self.driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            return False
    
    def _parse_units_from_windsor_page(self) -> Dict[str, dict]:
        """
        Parse available units from Windsor Communities floorplans page.
        Uses the Spaces plugin markup: article.spaces-unit elements with data attributes.
        
        Returns:
            Dictionary mapping unit numbers (e.g., '#758') to details including floor plan code
        """
        all_units: Dict[str, dict] = {}
        try:
            # Ensure we're on the Units tab
            url = self.url + ("&" if "?" in self.url else "?") + "spaces_tab=unit"
            self.driver.get(url)

            # Wait for unit cards to be present
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'article.spaces-unit'))
                )
            except Exception:
                # Fallback small sleep in case of slow load
                time.sleep(3)

            unit_cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                'article.spaces-unit[data-spaces-available="true"]'
            )

            for card in unit_cards:
                unit_num_raw = card.get_attribute('data-spaces-unit') or ''
                if not unit_num_raw:
                    # Fallback from aria-label like "Unit 758"
                    aria = card.get_attribute('aria-label') or ''
                    m = re.search(r'Unit\s*(\w+)', aria)
                    unit_num_raw = m.group(1) if m else ''

                if not unit_num_raw:
                    continue

                unit_num = unit_num_raw if str(unit_num_raw).startswith('#') else f"#{unit_num_raw}"
                plan_code = (card.get_attribute('data-spaces-sort-plan-name') or '').upper() or 'UNKNOWN'
                try:
                    beds_attr = card.get_attribute('data-spaces-sort-bed')
                    bedrooms = int(beds_attr) if beds_attr is not None else None
                except Exception:
                    bedrooms = None

                all_units[unit_num] = {
                    'unit': unit_num,
                    'floor_plan': plan_code,
                    'bedrooms': bedrooms,
                    'last_seen': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"⚠️  Failed to parse units from Windsor page: {e}")
        
        return all_units
    
    def fetch_available_units(self) -> Dict[str, dict]:
        """
        Fetch all available units from the Windsor Winchester floorplans page.
        
        Returns:
            Dictionary mapping unit numbers to their details
        """
        if not self.driver:
            if not self.setup_driver():
                return {}

        print("   Loading Windsor Winchester floorplans page...", flush=True)
        units = self._parse_units_from_windsor_page()

        # Optional filters
        if self.notify_floor_plans:
            units = {k: v for k, v in units.items() if v['floor_plan'] in self.notify_floor_plans}
        if self.notify_min_bedrooms is not None:
            units = {k: v for k, v in units.items() if v.get('bedrooms') is not None and v.get('bedrooms') >= self.notify_min_bedrooms}

        print(f"   ✓ Found {len(units)} available units")
        return units
    
    def compare_units(self, current: Dict[str, dict], previous: Dict[str, dict]) -> Dict[str, List]:
        """Compare current and previous unit data"""
        changes = {
            'new': [],
            'removed': []
        }
        
        current_units = set(current.keys())
        previous_units = set(previous.keys())
        
        # Find newly available units
        new_units = current_units - previous_units
        changes['new'] = [current[unit] for unit in sorted(new_units)]
        
        # Find units no longer available
        removed_units = previous_units - current_units
        changes['removed'] = [previous[unit] for unit in sorted(removed_units)]
        
        return changes
    
    def print_units(self, units: Dict[str, dict]):
        """Print unit information in a readable format"""
        print("\n" + "="*80)
        print(f"📊 Available Units ({len(units)} total)")
        print("="*80)
        
        if not units:
            print("⚠️  No units currently available.")
            return
        
        # Group by floor plan
        by_plan = {}
        for unit_num, info in units.items():
            plan = info['floor_plan']
            if plan not in by_plan:
                by_plan[plan] = []
            by_plan[plan].append(unit_num)
        
        # Print grouped by floor plan
        for plan in sorted(by_plan.keys()):
            unit_list = sorted(by_plan[plan])
            print(f"\n🏠 Floor Plan {plan} ({len(unit_list)} units):")
            # Print units in rows of 8
            for i in range(0, len(unit_list), 8):
                row = unit_list[i:i+8]
                print(f"   {', '.join(row)}")
    
    def print_changes(self, changes: Dict[str, List]):
        """Print changes in a readable format"""
        has_changes = any(changes.values())
        
        if not has_changes:
            return
        
        print("\n" + "🔔 " + "="*78)
        print("  CHANGES DETECTED!")
        print("="*80)
        
        if changes['new']:
            print(f"\n✨ NEW UNITS AVAILABLE ({len(changes['new'])}):")
            # Group by floor plan
            by_plan = {}
            for unit in changes['new']:
                plan = unit['floor_plan']
                if plan not in by_plan:
                    by_plan[plan] = []
                by_plan[plan].append(unit['unit'])
            
            for plan in sorted(by_plan.keys()):
                units = sorted(by_plan[plan])
                print(f"   Floor Plan {plan}: {', '.join(units)}")
        
        if changes['removed']:
            print(f"\n❌ UNITS NO LONGER AVAILABLE ({len(changes['removed'])}):")
            # Group by floor plan
            by_plan = {}
            for unit in changes['removed']:
                plan = unit['floor_plan']
                if plan not in by_plan:
                    by_plan[plan] = []
                by_plan[plan].append(unit['unit'])
            
            for plan in sorted(by_plan.keys()):
                units = sorted(by_plan[plan])
                print(f"   Floor Plan {plan}: {', '.join(units)}")
        
        print("\n" + "="*80)
    
    def save_to_file(self, units: Dict[str, dict], filename: str = "available_apartments.txt"):
        """Save available apartments to a text file"""
        try:
            # Save human-readable text file
            with open(filename, 'w') as f:
                f.write("="*80 + "\n")
                f.write("AVAILABLE APARTMENTS\n")
                f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Units: {len(units)}\n")
                f.write("="*80 + "\n\n")
                
                if not units:
                    f.write("No units currently available.\n")
                else:
                    # Group by floor plan
                    by_plan = {}
                    for unit_num, info in units.items():
                        plan = info['floor_plan']
                        if plan not in by_plan:
                            by_plan[plan] = []
                        by_plan[plan].append(unit_num)
                    
                    # Write grouped by floor plan
                    for plan in sorted(by_plan.keys()):
                        unit_list = sorted(by_plan[plan])
                        f.write(f"Floor Plan {plan} ({len(unit_list)} units):\n")
                        for unit in unit_list:
                            f.write(f"  {unit}\n")
                        f.write("\n")
            
            # Also save JSON for easy loading
            json_filename = filename.replace('.txt', '.json')
            with open(json_filename, 'w') as f:
                json.dump(units, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Warning: Could not save to file: {e}")
    
    def load_from_file(self, filename: str = "available_apartments.json") -> Dict[str, dict]:
        """Load previous apartments from JSON file"""
        try:
            if not os.path.exists(filename):
                return {}
            
            with open(filename, 'r') as f:
                units = json.load(f)
                return units
        except Exception as e:
            print(f"⚠️  Warning: Could not load from file: {e}")
            return {}
    
    def send_wechat_notification(self, title: str, content: str) -> bool:
        """
        Send WeChat notification using configured method
        
        Args:
            title: Notification title
            content: Notification content
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.wechat_token:
            return False
        
        try:
            if self.wechat_method == 'pushplus':
                return self._send_pushplus(title, content)
            elif self.wechat_method == 'serverchan':
                return self._send_serverchan(title, content)
            elif self.wechat_method == 'work':
                return self._send_wechat_work(title, content)
            else:
                print(f"⚠️  Unknown WeChat method: {self.wechat_method}")
                return False
        except Exception as e:
            print(f"⚠️  Failed to send WeChat notification: {e}")
            return False
    
    def _send_pushplus(self, title: str, content: str) -> bool:
        """Send notification via PushPlus"""
        url = 'http://www.pushplus.plus/send'
        data = {
            'token': self.wechat_token,
            'title': title,
            'content': content,
            'template': 'html'
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result.get('code') == 200
    
    def _send_serverchan(self, title: str, content: str) -> bool:
        """Send notification via Server酱 (ServerChan)"""
        url = f'https://sctapi.ftqq.com/{self.wechat_token}.send'
        data = {
            'title': title,
            'desp': content
        }
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        return result.get('code') == 0
    
    def _send_wechat_work(self, title: str, content: str) -> bool:
        """Send notification via WeChat Work (企业微信)"""
        url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.wechat_token}'
        data = {
            'msgtype': 'text',
            'text': {
                'content': f'{title}\n\n{content}'
            }
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result.get('errcode') == 0
    
    def filter_changes_by_floor_plan(self, changes: Dict[str, List]) -> Dict[str, List]:
        """Filter changes to only include specified floor plans"""
        if not self.notify_floor_plans:
            return changes
        
        filtered = {
            'new': [u for u in changes['new'] if u['floor_plan'] in self.notify_floor_plans],
            'removed': [u for u in changes['removed'] if u['floor_plan'] in self.notify_floor_plans]
        }
        return filtered
    
    def filter_units_by_floor_plan(self, units: Dict[str, dict]) -> Dict[str, dict]:
        """Filter units to only include specified floor plans"""
        if not self.notify_floor_plans:
            return units
        
        return {k: v for k, v in units.items() if v['floor_plan'] in self.notify_floor_plans}
    
    def send_email_notification(self, title: str, content: str) -> bool:
        """
        Send email notification to multiple recipients
        
        Args:
            title: Email subject
            content: Email content (HTML)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not all([self.email_to, self.email_from, self.smtp_server, self.smtp_password]):
            return False
        
        try:
            # Convert <br> to <br/> for proper HTML
            html_content = content.replace('<br>', '<br/>')
            
            # Create HTML email
            html_body = f"""
            <html>
              <head></head>
              <body>
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                  <h2 style="color: #2c3e50;">{title}</h2>
                  <div style="margin-top: 20px;">
                    {html_content}
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Send to each recipient
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.smtp_password)
                
                for recipient in self.email_to:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = title
                    msg['From'] = self.email_from
                    msg['To'] = recipient
                    
                    html_part = MIMEText(html_body, 'html')
                    msg.attach(html_part)
                    
                    server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"⚠️  Failed to send email: {e}")
            return False
    
    def format_notification(self, changes: Dict[str, List], current_units: Dict[str, dict]) -> tuple:
        """Format notification title and content with apartment numbers in title"""
        # Build title with specific apartment numbers
        title_parts = []
        
        if changes['new']:
            new_units = [u['unit'] for u in changes['new']]
            if len(new_units) <= 3:
                title_parts.append(f"✨ NEW: {', '.join(new_units)}")
            else:
                title_parts.append(f"✨ NEW: {', '.join(new_units[:3])} +{len(new_units)-3} more")
        
        if changes['removed']:
            removed_units = [u['unit'] for u in changes['removed']]
            if len(removed_units) <= 3:
                title_parts.append(f"❌ GONE: {', '.join(removed_units)}")
            else:
                title_parts.append(f"❌ GONE: {', '.join(removed_units[:3])} +{len(removed_units)-3} more")
        
        title = " | ".join(title_parts) if title_parts else "🏠 Apartment Update"
        
        # Build content with ALL current availability
        lines = []
        lines.append(f"<b>📊 ALL AVAILABLE UNITS ({len(current_units)} total)</b>:")
        lines.append("")
        
        # Group by floor plan
        by_plan = {}
        for unit_num, info in current_units.items():
            plan = info['floor_plan']
            if plan not in by_plan:
                by_plan[plan] = []
            by_plan[plan].append(unit_num)
        
        for plan in sorted(by_plan.keys()):
            units_str = ', '.join(sorted(by_plan[plan]))
            lines.append(f"Floor Plan {plan}: {units_str}")
        
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        content = '<br>'.join(lines)
        return title, content
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def run(self):
        """Main monitoring loop"""
        print(f"🚀 Starting Apartment Unit Monitor")
        print(f"📍 URL: {self.url}")
        print(f"⏱️  Check interval: {self.check_interval} seconds")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not SELENIUM_AVAILABLE:
            print("\n❌ Selenium is required but not installed")
            print("Install with: pip install selenium")
            sys.exit(1)
        
        print("\n🌐 Initializing browser...")
        if not self.setup_driver():
            sys.exit(1)
        
        print("✓ Browser ready")
        
        # Load previous units from file if available
        loaded_units = self.load_from_file()
        if loaded_units:
            self.previous_units = loaded_units
            print(f"✓ Loaded {len(loaded_units)} units from previous run")
        
        print(f"\nℹ️  Checking current availability from Windsor Winchester")
        print("   First check may take 30-60 seconds...")
        print("   Results will be saved to: available_apartments.txt")
        print("\nPress Ctrl+C to stop monitoring...")
        print("="*80)
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n⏰ Check #{iteration} at {timestamp}")
                
                # Fetch available units
                current_units = self.fetch_available_units()
                
                # Save to file
                self.save_to_file(current_units)
                
                if iteration == 1 and not self.previous_units:
                    # First run with no previous data - display current state
                    self.print_units(current_units)
                    self.previous_units = current_units
                    
                    # Send initial notification (filtered by floor plans)
                    if self.wechat_token and current_units:
                        notify_units = self.filter_units_by_floor_plan(current_units)
                        
                        if notify_units:
                            title = "🏠 Apartment Monitor Started"
                            if self.notify_floor_plans:
                                plans_str = ', '.join(self.notify_floor_plans)
                                lines = [f"✨ <b>Found {len(notify_units)} available units (Floor Plans: {plans_str})</b>:"]
                            else:
                                lines = [f"✨ <b>Found {len(notify_units)} available units</b>:"]
                            
                            by_plan = {}
                            for unit_num, info in notify_units.items():
                                plan = info['floor_plan']
                                if plan not in by_plan:
                                    by_plan[plan] = []
                                by_plan[plan].append(unit_num)
                            
                            for plan in sorted(by_plan.keys()):
                                units_str = ', '.join(sorted(by_plan[plan]))
                                lines.append(f"  Floor Plan {plan}: {units_str}")
                            
                            lines.append("")
                            lines.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            content = '<br>'.join(lines)
                            
                            notifications_sent = []
                            if self.send_wechat_notification(title, content):
                                notifications_sent.append("WeChat")
                            if self.send_email_notification(title, content):
                                notifications_sent.append("Email")
                            
                            if notifications_sent:
                                print(f"📱 Notifications sent: {', '.join(notifications_sent)} ({len(notify_units)} units)")
                            else:
                                print("⚠️  No notifications configured or all failed")
                        else:
                            print(f"ℹ️  No units match notification filter (Floor Plans: {', '.join(self.notify_floor_plans)})")
                else:
                    # Compare with previous state (either from file or previous check)
                    changes = self.compare_units(current_units, self.previous_units)
                    
                    if any(changes.values()):
                        self.print_changes(changes)
                        self.print_units(current_units)
                        
                        # Send change notification (filtered by floor plans)
                        if self.wechat_token or self.email_to:
                            filtered_changes = self.filter_changes_by_floor_plan(changes)
                            
                            if any(filtered_changes.values()):
                                notify_units = self.filter_units_by_floor_plan(current_units)
                                title, content = self.format_notification(filtered_changes, notify_units)
                                
                                notifications_sent = []
                                if self.send_wechat_notification(title, content):
                                    notifications_sent.append("WeChat")
                                if self.send_email_notification(title, content):
                                    notifications_sent.append("Email")
                                
                                if notifications_sent:
                                    total_changed = len(filtered_changes['new']) + len(filtered_changes['removed'])
                                    print(f"📱 Notifications sent: {', '.join(notifications_sent)} ({total_changed} changes)")
                                else:
                                    print("⚠️  No notifications configured or all failed")
                            else:
                                if self.notify_floor_plans:
                                    print(f"ℹ️  Changes detected but none match notification filter ({', '.join(self.notify_floor_plans)})")
                    else:
                        print(f"✓ No changes ({len(current_units)} units available)")
                    
                    self.previous_units = current_units
                
                # Wait for next check
                if iteration == 1:
                    print(f"\n💤 Waiting {self.check_interval} seconds until next check...")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            print(f"Total checks performed: {iteration}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n🧹 Cleaning up...")
            self.cleanup()
            sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Monitor apartment availability on Windsor Winchester',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (reads token from secrets/wechat_token.txt)
  python apartment_monitor.py
  
  # Specify WeChat notification method
  python apartment_monitor.py --wechat-method serverchan
  
  # Custom check interval
  python apartment_monitor.py --interval 30
  
  # Disable headless mode (show browser)
  python apartment_monitor.py --no-headless
        """
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=20,
        help='Check interval in seconds (default: 20)'
    )
    
    parser.add_argument(
        '--wechat-method',
        choices=['pushplus', 'serverchan', 'work'],
        default='pushplus',
        help='WeChat notification method (default: pushplus)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (default: headless mode)'
    )
    
    args = parser.parse_args()
    
    url = "https://www.windsorcommunities.com/properties/windsor-winchester/floorplans/"
    
    # Read WeChat token from secrets folder or environment variable
    wechat_token = None
    token_file = os.path.join(os.path.dirname(__file__), 'secrets', 'wechat_token.txt')
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                wechat_token = f.read().strip()
            print(f"✅ WeChat token loaded from: {token_file}")
        except Exception as e:
            print(f"⚠️  Failed to read token from {token_file}: {e}")
    
    # Fall back to environment variable
    if not wechat_token:
        wechat_token = os.environ.get('WECHAT_TOKEN')
        if wechat_token:
            print("✅ WeChat token loaded from environment variable")
    
    # Read email configuration from environment variables
    email_to = os.environ.get('EMAIL_TO')
    # Support comma-separated list in env var
    if email_to and ',' in email_to:
        email_to = [e.strip() for e in email_to.split(',')]
    
    email_from = os.environ.get('EMAIL_FROM')
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    # Or read from secrets/email_config.json
    email_config_file = os.path.join(os.path.dirname(__file__), 'secrets', 'email_config.json')
    if os.path.exists(email_config_file):
        try:
            with open(email_config_file, 'r') as f:
                email_config = json.load(f)
                email_to = email_to or email_config.get('email_to')
                email_from = email_from or email_config.get('email_from')
                smtp_server = smtp_server or email_config.get('smtp_server')
                smtp_port = smtp_port if smtp_port != 587 else email_config.get('smtp_port', 587)
                smtp_password = smtp_password or email_config.get('smtp_password')
            print(f"✅ Email config loaded from: {email_config_file}")
        except Exception as e:
            print(f"⚠️  Failed to read email config from {email_config_file}: {e}")
    
    # Only notify for 2+ bedroom homes by default
    notify_floor_plans = None  # e.g., ['A','B'] if you want to filter by plan letters
    notify_min_bedrooms = 2
    
    # Print configuration status
    notifications_enabled = []
    if wechat_token:
        notifications_enabled.append(f"WeChat ({args.wechat_method})")
    if email_to and email_from and smtp_server and smtp_password:
        if isinstance(email_to, list):
            recipients_str = ', '.join(email_to)
            notifications_enabled.append(f"Email ({len(email_to)} recipients: {recipients_str})")
        else:
            notifications_enabled.append(f"Email (to: {email_to})")
    
    if notifications_enabled:
        print(f"✅ Notifications enabled: {', '.join(notifications_enabled)}")
        filter_parts = []
        if notify_floor_plans:
            filter_parts.append(f"Plans {', '.join(notify_floor_plans)}")
        if notify_min_bedrooms is not None:
            filter_parts.append(f"{notify_min_bedrooms}+ bedrooms")
        print(f"ℹ️  Notification filter: {('; '.join(filter_parts)) if filter_parts else 'none'}")
    else:
        print("ℹ️  No notifications configured")
        print("   - WeChat: add token to secrets/wechat_token.txt")
        print("   - Email: create secrets/email_config.json with email settings")
    
    monitor = ApartmentMonitor(
        url, 
        args.interval, 
        headless=not args.no_headless, 
        wechat_token=wechat_token, 
        wechat_method=args.wechat_method,
        notify_floor_plans=notify_floor_plans,
        notify_min_bedrooms=notify_min_bedrooms,
        email_to=email_to,
        email_from=email_from,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_password=smtp_password
    )
    monitor.run()


if __name__ == "__main__":
    main()
