# WeChat Notifications Setup Guide

Your apartment monitor now supports WeChat notifications! You'll receive alerts when:
- ✅ The monitor starts (first check with available apartments)
- ✅ New apartments become available
- ✅ Apartments are removed/rented

---

## 🚀 Quick Start (3 Methods)

### **Method 1: PushPlus (Easiest - Recommended)** ⭐

**No registration, just scan QR code!**

1. **Get Your Token:**
   - Visit: http://www.pushplus.plus/
   - Click "一对一推送" (One-to-One Push)
   - Scan QR code with WeChat to follow the official account
   - Copy your token (looks like: `abc123def456...`)

2. **Set Environment Variable:**
   ```bash
   export WECHAT_TOKEN='your_pushplus_token_here'
   export WECHAT_METHOD='pushplus'
   ```

3. **Run the monitor:**
   ```bash
   cd /path/to/apartment-monitor
   python apartment_monitor.py
   ```

4. **You're done!** Check WeChat for notifications 🎉

---

### **Method 2: Server酱 (ServerChan)**

**Simple, with GitHub login**

1. **Get Your Token:**
   - Visit: https://sct.ftqq.com/
   - Login with GitHub
   - Click "发送消息" → "SendKey"
   - Copy your SendKey (looks like: `SCT12345...`)

2. **Bind WeChat:**
   - In Server酱 dashboard, click "微信配置"
   - Scan QR code with WeChat

3. **Set Environment Variable:**
   ```bash
   export WECHAT_TOKEN='your_sendkey_here'
   export WECHAT_METHOD='serverchan'
   ```

4. **Run the monitor:**
   ```bash
   python apartment_monitor.py
   ```

---

### **Method 3: WeChat Work (企业微信)**

**For power users, more features**

1. **Create a WeChat Work Account:**
   - Visit: https://work.weixin.qq.com/
   - Register (free)
   
2. **Create a Group Robot:**
   - In WeChat Work, create a group chat
   - Add a "群机器人" (Group Robot)
   - Get the Webhook URL (contains a key)
   
3. **Extract the Key:**
   - URL format: `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY`
   - Copy only the `YOUR_KEY` part

4. **Set Environment Variable:**
   ```bash
   export WECHAT_TOKEN='your_webhook_key_here'
   export WECHAT_METHOD='work'
   ```

5. **Run the monitor:**
   ```bash
   python apartment_monitor.py
   ```

---

## 📝 Full Example

```bash
# 1. Set your token (choose one method)
export WECHAT_TOKEN='abc123def456ghi789'
export WECHAT_METHOD='pushplus'

# 2. Run the monitor
cd /path/to/apartment-monitor
python apartment_monitor.py

# 3. You'll see:
# ✅ WeChat notifications enabled (Method: pushplus)
# 🚀 Starting Apartment Unit Monitor
# ...
# 📱 WeChat notification sent
```

---

## 🔧 Run Without Notifications

If you don't set `WECHAT_TOKEN`, the script runs normally without notifications:

```bash
# Just run it
python apartment_monitor.py

# Output:
# ℹ️  WeChat notifications disabled (set WECHAT_TOKEN to enable)
```

---

## 🧪 Test Your Setup

Create a test script to verify WeChat notifications work:

```python
# test_wechat.py
import os
from apartment_monitor import ApartmentMonitor

# Set your token
os.environ['WECHAT_TOKEN'] = 'your_token_here'
os.environ['WECHAT_METHOD'] = 'pushplus'

# Create monitor
monitor = ApartmentMonitor('https://example.com', 20)

# Send test notification
title = "🧪 Test Notification"
content = "If you see this, WeChat notifications are working!<br>✅ All systems go!"

if monitor.send_wechat_notification(title, content):
    print("✅ Test notification sent successfully!")
else:
    print("❌ Failed to send notification. Check your token.")
```

Run it:
```bash
python test_wechat.py
```

---

## 💡 Permanent Setup (Recommended)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# WeChat Notifications for Apartment Monitor
export WECHAT_TOKEN='your_token_here'
export WECHAT_METHOD='pushplus'
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

Now you can run the monitor anytime without setting variables!

---

## 🎨 Notification Examples

### First Check (No Previous Data)
```
🏠 Apartment Monitor Started

✨ Found 22 available units:
  Floor Plan A: #758
  Floor Plan B: #695
  Floor Plan C: #636
  ...
  
🕐 2025-10-07 13:48:24
```

### New Apartments Available
```
🏠 Apartment Availability Update

✨ NEW UNITS (3):
  Floor Plan D: #123
  Floor Plan E: #456, #789

📊 Total Available: 25 units
🕐 2025-10-07 14:15:30
```

### Apartments Removed
```
🏠 Apartment Availability Update

❌ REMOVED (2):
  Floor Plan A: #758
  Floor Plan B: #695

📊 Total Available: 20 units
🕐 2025-10-07 14:30:45
```

---

## ❓ Troubleshooting

**Q: I'm not receiving notifications**
- Check that your token is correct
- Verify you've followed the official account/robot on WeChat
- Test with `test_wechat.py` script above

**Q: Can I use multiple notification methods?**
- Not simultaneously, but you can change `WECHAT_METHOD` anytime

**Q: Are notifications secure?**
- PushPlus/ServerChan: Messages sent through their servers
- WeChat Work: Direct to Tencent's servers, more secure

**Q: Is there a rate limit?**
- PushPlus: 200 messages/day (free tier)
- ServerChan: 5 messages/minute
- WeChat Work: 20 messages/minute per robot

---

## 📚 Summary

| Method | Difficulty | Setup Time | Best For |
|--------|------------|------------|----------|
| **PushPlus** | ⭐ Easiest | 2 minutes | Personal use |
| **ServerChan** | ⭐⭐ Easy | 3 minutes | GitHub users |
| **WeChat Work** | ⭐⭐⭐ Medium | 10 minutes | Power users |

**Recommendation:** Start with **PushPlus** - it's the simplest and works great for personal use!

---

Happy apartment hunting! 🏠✨

