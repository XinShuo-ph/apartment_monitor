# Apartment Availability Monitor

Automated apartment availability monitoring for Windsor Winchester apartments. Sends real-time notifications via WeChat and Email when apartments become available or are removed.

## Features

✨ **Real-time Monitoring**
- Checks apartment availability every 20 seconds
- Monitors all floor plans (A-V)
- Tracks specific unit numbers (e.g., #758, #322, #410)

📱 **Multi-channel Notifications**
- **WeChat** via PushPlus (instant mobile notifications)
- **Email** via Gmail SMTP (detailed notifications to multiple recipients)
- Customizable notification filters (e.g., only 2+ bedroom units)

🎯 **Smart Change Detection**
- Detects newly available apartments
- Alerts when apartments are removed/rented
- Shows apartment numbers directly in notification titles
- Displays full availability list in notification body

💾 **Persistent State**
- Saves availability data locally
- Resumes monitoring after restarts
- Detects changes even after script restart

## Quick Start

### Prerequisites

- Python 3.7+
- Chrome browser
- Chromedriver (on macOS: `brew install chromedriver`)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd misc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Fix macOS Gatekeeper (if needed):
```bash
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

### Configuration

#### WeChat Notifications (PushPlus)

1. Visit http://www.pushplus.plus/ and login with WeChat
2. Copy your token
3. Create `secrets/wechat_token.txt`:
```bash
mkdir -p secrets
echo "your-pushplus-token" > secrets/wechat_token.txt
```

See [WECHAT_SETUP.md](WECHAT_SETUP.md) for detailed instructions.

#### Email Notifications (Gmail)

1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Create `secrets/email_config.json`:
```json
{
  "email_to": [
    "your-email@example.com",
    "another@example.com"
  ],
  "email_from": "your-gmail@gmail.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_password": "your-16-char-app-password"
}
```

See [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed instructions.

### Usage

**Basic usage:**
```bash
python apartment_monitor.py
```

**Custom check interval:**
```bash
python apartment_monitor.py --interval 30
```

**Change WeChat method:**
```bash
python apartment_monitor.py --wechat-method serverchan
```

**Show browser (debug mode):**
```bash
python apartment_monitor.py --no-headless
```

**Override the floorplans URL:**
```bash
python apartment_monitor.py --url https://windsorwinchester.com/floorplans/
```

You can also set the URL via environment variable:
```bash
export APARTMENT_URL="https://windsorwinchester.com/floorplans/"
python apartment_monitor.py
```

**View all options:**
```bash
python apartment_monitor.py --help
```

### Testing

**Test WeChat notifications:**
```bash
python test_wechat.py
```

**Test email notifications:**
```bash
python test_email.py
```

## Notification Examples

### New Apartments Available
**WeChat/Email Title:**
```
✨ NEW: #328, #410
```

**Body:**
```
📊 ALL AVAILABLE UNITS (22 total)

Floor Plan A: #758
Floor Plan B: #695
Floor Plan N: #322
Floor Plan O: #328, #410
Floor Plan U: #499

🕐 2025-10-07 14:30:00
```

### Apartments Removed
**Title:**
```
❌ GONE: #758 | ✨ NEW: #328
```

## Customization

### Notification Filter

By default, only notifies for 2+ bedroom floor plans (N, O, P, Q, R, S, T, U, V).

To modify, edit `apartment_monitor.py`:
```python
notify_floor_plans = ['N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V']
```

### Check Interval

Default: 20 seconds

Change via command line:
```bash
python apartment_monitor.py --interval 60
```

## File Structure

```
.
├── apartment_monitor.py       # Main monitoring script
├── requirements.txt           # Python dependencies
├── test_email.py             # Email notification test
├── test_wechat.py            # WeChat notification test
├── WECHAT_SETUP.md           # WeChat setup guide
├── GMAIL_SETUP.md            # Gmail setup guide
├── secrets/                  # Configuration (not in git)
│   ├── wechat_token.txt
│   ├── email_config.json
│   └── email_config.json.example
├── available_apartments.json # Current state (auto-generated)
└── available_apartments.txt  # Human-readable list (auto-generated)
```

## Troubleshooting

### Chrome/Chromedriver Issues

**macOS Gatekeeper blocking chromedriver:**
```bash
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

**Chromedriver version mismatch:**
```bash
brew upgrade chromedriver
```

### WeChat Notifications Not Working

- Verify token is correct
- Check that you've followed the PushPlus official account on WeChat
- Test with `python test_wechat.py`

### Email Notifications Not Working

- Ensure you're using App Password, not regular Gmail password
- Verify 2-Step Verification is enabled
- Check SMTP settings are correct
- Test with `python test_email.py`

### No Apartments Detected

- Check your internet connection
- Verify the website is accessible: https://windsorwinchester.com/floorplans/
- Run with `--no-headless` to see browser activity

## Technologies Used

- **Selenium** - Browser automation for JavaScript-rendered content
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP client for notifications
- **SMTPLib** - Email sending

## Security Notes

🔒 **Never commit secrets!**
- The `secrets/` folder is in `.gitignore`
- Never share your tokens or passwords
- Use App Passwords for Gmail (not your main password)

## License

MIT License - feel free to use and modify for your needs.

## Contributing

Found a bug? Have a feature request? Open an issue or submit a pull request!

---

Happy apartment hunting! 🏠✨

