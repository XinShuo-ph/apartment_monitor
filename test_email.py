#!/usr/bin/env python3
"""
Test script to send email from Gmail
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def send_test_email(gmail_address, gmail_app_password, recipients=None):
    """Send a test email from Gmail to specified recipients"""
    
    # Email configuration
    email_from = gmail_address
    if recipients is None:
        recipients = ["recipient@example.com"]
    elif isinstance(recipients, str):
        recipients = [recipients]
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    print("="*60)
    print("📧 Gmail Email Test")
    print("="*60)
    print(f"From: {email_from}")
    print(f"To: {', '.join(recipients)}")
    print(f"SMTP: {smtp_server}:{smtp_port}")
    print("="*60)
    
    try:
        # Create message
        # Create HTML content
        html_content = """
        <html>
          <head></head>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c3e50;">🧪 Email Test Successful!</h2>
            <div style="margin-top: 20px;">
              <p><b>This is a test email from your Apartment Monitor script.</b></p>
              <br/>
              <p>If you're seeing this, your Gmail SMTP configuration is working correctly! ✅</p>
              <br/>
              <p>Your apartment monitor is now ready to send you email notifications when:</p>
              <ul>
                <li>✨ New apartments become available</li>
                <li>❌ Apartments are removed/rented</li>
              </ul>
              <br/>
              <p style="color: #7f8c8d; font-size: 12px;">
                Sent at: 2025-10-07 14:30:00
              </p>
            </div>
          </body>
        </html>
        """
        
        # Connect and send to all recipients
        print("\n📤 Connecting to Gmail SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("🔐 Starting TLS encryption...")
            server.starttls()
            
            print("🔑 Logging in...")
            server.login(email_from, gmail_app_password)
            
            print(f"📨 Sending email to {len(recipients)} recipient(s)...")
            for recipient in recipients:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = "🧪 Test Email - Apartment Monitor"
                msg['From'] = email_from
                msg['To'] = recipient
                
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
                
                server.send_message(msg)
                print(f"   ✓ Sent to {recipient}")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Email(s) sent successfully!")
        print("="*60)
        print(f"\nCheck inbox(es) for the test email:")
        for recipient in recipients:
            print(f"  - {recipient}")
        print("(It may take a few seconds to arrive)")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n" + "="*60)
        print("❌ AUTHENTICATION FAILED")
        print("="*60)
        print("\nPossible issues:")
        print("1. Wrong Gmail address or App Password")
        print("2. Need to use App Password (not regular password)")
        print("3. 2-Step Verification not enabled")
        print("\nHow to fix:")
        print("1. Go to: https://myaccount.google.com/security")
        print("2. Enable 2-Step Verification")
        print("3. Go to: https://myaccount.google.com/apppasswords")
        print("4. Create an App Password for 'Mail'")
        print("5. Use that 16-character password")
        return False
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR")
        print("="*60)
        print(f"\n{type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("- Check your internet connection")
        print("- Verify Gmail address is correct")
        print("- Make sure you're using App Password, not regular password")
        return False


def main():
    print("\n" + "="*60)
    print("Gmail SMTP Test for Apartment Monitor")
    print("="*60)
    
    # Get credentials
    print("\nPlease enter your Gmail credentials:")
    print("(Your App Password will not be displayed)")
    print()
    
    gmail_address = input("Gmail address: ").strip()
    
    if not gmail_address:
        print("❌ Error: Gmail address is required")
        sys.exit(1)
    
    # Get password securely
    try:
        import getpass
        gmail_app_password = getpass.getpass("Gmail App Password: ").strip()
    except ImportError:
        gmail_app_password = input("Gmail App Password: ").strip()
    
    if not gmail_app_password:
        print("❌ Error: App Password is required")
        sys.exit(1)
    
    print()
    
    # Send test email
    success = send_test_email(gmail_address, gmail_app_password)
    
    if success:
        print("\n✅ Your Gmail SMTP is configured correctly!")
        print("\nTo use with the apartment monitor:")
        print("1. Create: secrets/email_config.json")
        print("2. Add this content:")
        print(f'''
{{
  "email_to": [
    "recipient1@example.com",
    "recipient2@example.com"
  ],
  "email_from": "{gmail_address}",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_password": "YOUR_APP_PASSWORD_HERE"
}}
''')
        print("3. Run: python apartment_monitor.py")
        print("\nNote: email_to can be a single string or list of multiple recipients")
    else:
        print("\n❌ Please fix the issues above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()

