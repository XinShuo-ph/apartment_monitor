# Linux Server Deployment Guide

This guide covers deploying the apartment monitor on a Linux server (Ubuntu/Debian).

## Prerequisites

- Linux server with SSH access
- Python 3.7 or higher
- sudo/root access for installation

---

## Step 1: Install Chrome/Chromium

### Ubuntu/Debian:

```bash
# Update package list
sudo apt-get update

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb


# Verify installation
google-chrome --version
```

---

## Step 2: Install ChromeDriver

ChromeDriver version should match your Chrome version.

```bash
# Check your Chrome version first
google-chrome --version
# Example output: Google Chrome 141.0.7390.65

# Download matching ChromeDriver from:
# https://googlechromelabs.github.io/chrome-for-testing/

# For Chrome 141.0.7390.65:
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/141.0.7390.65/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Verify
chromedriver --version
```

---

## Step 3: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2

```
