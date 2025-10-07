# Gmail Email Notifications Setup

## Quick Setup (5 minutes)

### Step 1: Enable 2-Step Verification (Required)

1. Go to: https://myaccount.google.com/security
2. Under "Signing in to Google" → Click "2-Step Verification"
3. Follow the prompts to enable it (usually requires phone verification)

### Step 2: Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Under "Select app" → Choose "Mail"
3. Under "Select device" → Choose "Other" and enter "Apartment Monitor"
4. Click "Generate"
5. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)
   - ⚠️ Save this somewhere - you won't see it again!

### Step 3: Test Email Configuration

Run the test script:

```bash
cd /path/to/apartment-monitor
python test_email.py
```

Enter your Gmail address and the App Password when prompted.

**Expected output:**
```
✅ SUCCESS! Email sent successfully!
```

Check your inbox for the test email.

### Step 4: Configure Apartment Monitor

Create the configuration file:

```bash
cp secrets/email_config.json.example secrets/email_config.json
```

Edit `secrets/email_config.json`:

```json
{
  "email_to": "recipient@example.com",
  "email_from": "your-actual-gmail@gmail.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_password": "abcd efgh ijkl mnop"
}
```

Replace:
- `your-actual-gmail@gmail.com` with your Gmail address
- `abcd efgh ijkl mnop` with your App Password (remove spaces)

### Step 5: Run the Monitor

```bash
python apartment_monitor.py
```

You should see:
```
✅ Notifications enabled: WeChat (pushplus), Email (to: recipient@example.com)
```

---

## Gmail SMTP Settings Reference

| Setting | Value |
|---------|-------|
| **SMTP Server** | `smtp.gmail.com` |
| **Port** | `587` (TLS recommended) |
| **Security** | STARTTLS |
| **Username** | Your full Gmail address |
| **Password** | App Password (16 characters) |

---

## Troubleshooting

### ❌ "Authentication Failed"

**Cause:** Wrong credentials or App Password not created

**Fix:**
1. Make sure you're using **App Password**, not your regular Gmail password
2. Verify 2-Step Verification is enabled
3. Generate a new App Password if needed
4. Remove spaces from App Password (use `abcdefghijklmnop`, not `abcd efgh ijkl mnop`)

### ❌ "Connection Timeout"

**Cause:** Network or firewall blocking SMTP

**Fix:**
1. Check your internet connection
2. Try port 465 (SSL) instead of 587 (TLS)
3. Check if firewall is blocking outgoing SMTP

### ❌ "Less Secure Apps"

**Note:** Google removed "Less Secure Apps" option in 2022. You **must** use App Passwords now.

### 📧 Email Goes to Spam

If emails go to spam folder:
1. Mark one email as "Not Spam"
2. Add the sender to your contacts
3. Create a filter to always deliver to inbox

---

## Email Notification Format

When apartments change, you'll receive emails like:

**Subject:**
```
✨ NEW: #328, #410 | ❌ GONE: #758
```

**Body:**
```
📊 ALL AVAILABLE UNITS (22 total)

Floor Plan N: #322
Floor Plan O: #328, #410
Floor Plan U: #499

🕐 2025-10-07 14:30:00
```

---

## Using Both WeChat and Email

The monitor supports **both simultaneously**:
- WeChat via PushPlus (instant, mobile)
- Email via Gmail (detailed, searchable)

Both will be sent for every change detected!

---

## Security Notes

🔐 **Your App Password is sensitive!**
- Never commit `email_config.json` to git
- The `secrets/` folder is already in `.gitignore`
- If compromised, revoke it at: https://myaccount.google.com/apppasswords

✅ **App Passwords are safer than regular passwords:**
- Limited to one app (email only)
- Can be revoked anytime
- Doesn't give access to your full Google Account

---

## Alternative: Use PushPlus for Email Too

Instead of Gmail SMTP, you can configure email in PushPlus:

1. Login to http://www.pushplus.plus/
2. Go to "消息渠道" (Message Channels)
3. Add your email address
4. PushPlus will send to both WeChat and email automatically

**Pros:** Simpler, no SMTP configuration
**Cons:** Less control, depends on PushPlus service

---

Happy apartment hunting! 🏠✨

