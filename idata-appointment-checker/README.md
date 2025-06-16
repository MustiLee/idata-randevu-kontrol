# IDATA Italy Visa Appointment Checker

A Python console application that automatically checks for Italy visa appointment availability at IDATA Turkey offices (Istanbul).

## Features

- 🔄 Automated appointment checking every 10 minutes
- 🧩 Automatic captcha solving using OCR
- 📱 Telegram notifications when appointments become available
- 📧 Email notifications support
- 🔍 Checks both Altunizade and Gayrettepe offices
- 📝 Comprehensive logging
- ⚙️ Fully configurable via environment variables

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- Tesseract OCR

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd idata-appointment-checker
```

### 2. Create virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install system dependencies

#### macOS
```bash
brew install tesseract
brew install --cask chromedriver
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install chromium-chromedriver
```

#### Windows
- Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Download [ChromeDriver](https://chromedriver.chromium.org/) and add to PATH

### 5. Configure the application

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# General Configuration
CHECK_INTERVAL_MINUTES=10
HEADLESS_BROWSER=true
LOG_LEVEL=INFO

# Telegram Configuration (optional)
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email Configuration (optional)
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com

# Appointment Configuration
RESIDENCE_CITY=İstanbul
IDATA_OFFICES=Altunizade,Gayrettepe
TRAVEL_PURPOSE=Tourism
SERVICE_TYPE=Standard
NUM_PERSONS=3
```

## Configuration Guide

### Telegram Setup

1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Set `TELEGRAM_ENABLED=true` and add your credentials

### Email Setup (Gmail)

1. Enable 2-factor authentication on your Gmail account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in `EMAIL_SMTP_PASSWORD`
4. Set `EMAIL_ENABLED=true`

## Usage

Run the application:

```bash
python main.py
```

The application will:
1. Start with an initial appointment check
2. Schedule checks every 10 minutes (configurable)
3. Send notifications when appointments become available
4. Log all activities to `appointment_checker.log`

Stop the application with `Ctrl+C`.

## How It Works

1. **Main Page Navigation**: The bot navigates to the IDATA main page
2. **Captcha Solving**: Uses OCR (Tesseract) to automatically solve image-based captchas
3. **Form Submission**: Fills the appointment form with your configured preferences
4. **Availability Check**: Checks if the response contains appointment slots
5. **Notification**: Sends immediate notifications via enabled channels when slots are found

## Notification Messages

### When appointments are available:
- **Subject**: "✅ Italy Visa Appointments Available!"
- **Content**: Details about available time slots

### When errors occur:
- **Subject**: "❌ IDATA Appointment Checker Error"
- **Content**: Error details for troubleshooting

## Troubleshooting

### Common Issues

1. **Captcha solving failures**
   - Ensure Tesseract is properly installed
   - Check if the captcha format has changed
   - Try running with `HEADLESS_BROWSER=false` to debug

2. **Chrome driver issues**
   - Update ChromeDriver to match your Chrome version
   - Ensure ChromeDriver is in PATH

3. **Connection timeouts**
   - Check your internet connection
   - The IDATA website might be temporarily down

### Logs

Check `appointment_checker.log` for detailed information about:
- Appointment check results
- Captcha solving attempts
- Form submission status
- Error messages

## Project Structure

```
idata-appointment-checker/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration loader
│   ├── captcha/           # Captcha solving module
│   │   ├── __init__.py
│   │   └── solver.py
│   ├── scraper/           # Web scraping module
│   │   ├── __init__.py
│   │   └── appointment_checker.py
│   ├── notifier/          # Notification module
│   │   ├── __init__.py
│   │   └── notifier.py
│   └── scheduler/         # Task scheduling module
│       ├── __init__.py
│       └── scheduler.py
├── .env.example           # Example configuration
├── .gitignore
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Security Notes

- Never commit your `.env` file containing credentials
- Use strong passwords for email accounts
- Keep your Telegram bot token private
- Run the application on a secure, trusted network

## License

This project is for educational purposes. Please use responsibly and in accordance with IDATA's terms of service.

## Disclaimer

This tool is not affiliated with IDATA or the Italian government. Use at your own risk. The authors are not responsible for any consequences of using this tool.