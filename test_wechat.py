#!/usr/bin/env python3
"""
Quick test script for WeChat notifications
"""

import os
import sys

# Check if token is set
if 'WECHAT_TOKEN' not in os.environ:
    print("❌ Error: WECHAT_TOKEN not set!")
    print("\nPlease set it first:")
    print("  export WECHAT_TOKEN='your_token_here'")
    print("  export WECHAT_METHOD='pushplus'  # or 'serverchan' or 'work'")
    sys.exit(1)

from apartment_monitor import ApartmentMonitor

print("🧪 Testing WeChat Notification")
print("="*50)
print(f"Token: {os.environ['WECHAT_TOKEN'][:10]}...")
print(f"Method: {os.environ.get('WECHAT_METHOD', 'pushplus')}")
print("="*50)

# Create monitor instance
monitor = ApartmentMonitor(
    url='https://example.com', 
    check_interval=20,
    wechat_token=os.environ['WECHAT_TOKEN'],
    wechat_method=os.environ.get('WECHAT_METHOD', 'pushplus')
)

# Send test notification
print("\n📤 Sending test notification...")

title = "🧪 Apartment Monitor - Test"
content = """
<b>✅ WeChat notifications are working!</b><br>
<br>
Your apartment monitor is ready to send you alerts when:<br>
• New apartments become available<br>
• Apartments are removed/rented<br>
• The monitor starts up<br>
<br>
🕐 Test sent at: 2025-10-07 14:00:00
"""

success = monitor.send_wechat_notification(title, content)

print()
if success:
    print("✅ SUCCESS! Check your WeChat for the test message.")
    print("\nYour monitor is ready to use!")
    print("\nTo start monitoring:")
    print("  python apartment_monitor.py")
else:
    print("❌ FAILED to send notification.")
    print("\nTroubleshooting:")
    print("  1. Check your token is correct")
    print("  2. Verify you've followed the official account on WeChat")
    print("  3. Make sure you selected the right method (pushplus/serverchan/work)")
    print("  4. Check your internet connection")

print()

