#!/usr/bin/env python3
"""
Simple test bot to verify token and messaging
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Your bot token
BOT_TOKEN = "7548481068:AAGu39H2aOC5W0ml6Cnoc0rFuLMR4406BCw"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a simple test message."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    logging.info(f"Received /start from {user.username or user.first_name} (ID: {chat_id})")
    
    try:
        # Simple message without markdown
        message = f"Hello! This is a test message. Your chat ID is: {chat_id}"
        await update.message.reply_text(message)
        logging.info(f"Test message sent to {chat_id}")
        
        # Try with markdown
        markdown_message = "*Bold test* and _italic test_"
        await update.message.reply_text(markdown_message, parse_mode='Markdown')
        logging.info(f"Markdown message sent to {chat_id}")
        
    except Exception as e:
        logging.error(f"Error sending message: {e}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    logging.info(f"Received message '{text}' from chat_id: {chat_id}")
    
    try:
        await update.message.reply_text(f"You said: {text}")
        logging.info(f"Echo sent to {chat_id}")
    except Exception as e:
        logging.error(f"Error echoing message: {e}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("echo", echo))

    # Run the bot
    logging.info("Starting test bot...")
    application.run_polling()

if __name__ == '__main__':
    main()