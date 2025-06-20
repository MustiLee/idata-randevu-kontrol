# 🤖 IDATA Appointment Checker Bot - User Guide

## Overview
This Telegram bot monitors Italy visa appointments at IDATA offices in Istanbul and sends instant notifications when slots become available.

## 🏢 Monitored Offices
- **Altunizade Office**
- **Gayrettepe Office**

## 📱 Bot Commands

### `/start` - Subscribe to Notifications
When users send `/start`, they receive a comprehensive welcome message and are added to the database.

**New User Response:**
```
🎉 Welcome [Username]!

✅ You have been successfully subscribed to Italy visa appointment updates.

🔔 You will receive instant notifications when appointments become available at:
• Altunizade Office
• Gayrettepe Office

📱 Available Commands:
• /status - Check your subscription status
• /stop - Unsubscribe from updates

⚡ The bot is now monitoring appointments for you!
```

**Existing User Response:**
```
ℹ️ Hello [Username]!

You are already subscribed to appointment updates.

📅 Subscribed since: 2025-06-20 14:45

📱 Available Commands:
• /status - Check subscription details
• /stop - Unsubscribe from updates

⚡ The bot is actively monitoring appointments for you!
```

### `/stop` - Unsubscribe from Notifications
Users can unsubscribe anytime using this command.

**Successful Unsubscription:**
```
👋 Goodbye [Username]!

❌ You have been successfully unsubscribed from Italy visa appointment updates.

📭 You will no longer receive notifications about available appointments.

💡 Want to subscribe again?
Just send /start anytime to reactivate your subscription.

Thank you for using the IDATA Appointment Checker! 🇮🇹
```

**Not Subscribed Response:**
```
ℹ️ Hello [Username]!

You are not currently subscribed to appointment updates.

💡 Want to get notified about appointments?
Send /start to subscribe and receive instant notifications when Italy visa appointments become available!
```

### `/status` - Check Subscription Status
Shows detailed subscription information.

**Subscribed User Status:**
```
📊 Status Report for [Username]

✅ Status: Subscribed to updates
🔔 Monitoring: Altunizade & Gayrettepe offices
👥 Total subscribers: 15
📅 Subscribed since: 2025-06-20 14:45

📱 Available Commands:
• /stop - Unsubscribe from updates

⚡ You will be notified instantly when appointments become available!
```

**Not Subscribed Status:**
```
📊 Status Report for [Username]

❌ Status: Not subscribed
👥 Total subscribers: 15

💡 Want to get notified?
Send /start to subscribe and receive instant notifications about Italy visa appointments!
```

### `/help` - Show Help Information
Provides comprehensive bot usage instructions.

```
🤖 IDATA Appointment Checker Bot Help

Hello [Username]! This bot monitors Italy visa appointments at IDATA offices and sends instant notifications when slots become available.

🏢 Monitored Offices:
• Altunizade Office
• Gayrettepe Office

📱 Available Commands:

/start - Subscribe to appointment notifications
/stop - Unsubscribe from notifications
/status - Check your subscription status
/help - Show this help message

⚡ How it works:
1. Send /start to subscribe
2. The bot checks for appointments every 15 minutes
3. You get instant notifications when appointments are found
4. Send /stop anytime to unsubscribe

🇮🇹 Good luck with your Italy visa application!
```

## 🔔 Appointment Notification Messages
When appointments become available, all subscribed users receive:

```
🔔 ✅ Italy Visa Appointments Available!

Great news! Italy visa appointments are now available.

[Appointment details and availability information]

Act quickly as appointments may fill up fast!
```

## 🗄️ Database Features

### User Management
- **PostgreSQL Integration**: All user data stored in database with timestamps
- **Subscription Tracking**: Records when users subscribe/unsubscribe
- **Soft Deletes**: Users can resubscribe and maintain history
- **Automatic Cleanup**: Removes blocked/inactive users automatically

### Database Schema
```sql
CREATE TABLE telegram_users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    unsubscribed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Deployment Options

### Option 1: Docker with PostgreSQL
```bash
# Start PostgreSQL database
docker-compose up postgres -d

# Run application
docker-compose up appointment-checker
```

### Option 2: Local with Docker Database
```bash
# Start PostgreSQL database
docker-compose up postgres -d

# Run locally
python main.py
```

### Option 3: Local with JSON fallback
Set `DATABASE_ENABLED=false` in `.env` file to use JSON file storage.

## ⚙️ Configuration

### Required Environment Variables
```bash
# Telegram Configuration
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_fallback_chat_id

# Database Configuration (Optional)
DATABASE_ENABLED=true
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=idata_appointment_checker
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Appointment Configuration
RESIDENCE_CITY=İstanbul
IDATA_OFFICES=Altunizade,Gayrettepe
TRAVEL_PURPOSE=Tourism
SERVICE_TYPE=Standard
NUM_PERSONS=3
```

## 📊 User Experience Flow

1. **Discovery**: User finds the bot and sends `/help` or `/start`
2. **Subscription**: User sends `/start` and receives detailed welcome message
3. **Monitoring**: Bot checks appointments every 15 minutes
4. **Notification**: Instant alerts when appointments are available
5. **Management**: User can check status with `/status` or unsubscribe with `/stop`
6. **Re-subscription**: Users can easily resubscribe with `/start`

## 🔧 Technical Features

- **Multi-user Support**: Unlimited subscribers
- **Real-time Notifications**: Instant appointment alerts
- **Robust Error Handling**: Graceful fallbacks and error recovery
- **Database Integration**: PostgreSQL with JSON fallback
- **User-friendly Messages**: Clear, informative bot responses
- **Automatic Migration**: JSON to database migration on startup
- **Health Monitoring**: Removes inactive/blocked users automatically

This bot provides a professional, user-friendly experience for monitoring Italy visa appointments with comprehensive database tracking and clear communication at every step.