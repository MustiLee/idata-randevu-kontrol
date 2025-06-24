#!/usr/bin/env python3
"""
Debug bot to find where messages are going
"""

import logging
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

BOT_TOKEN = "7548481068:AAGu39H2aOC5W0ml6Cnoc0rFuLMR4406BCw"

async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send debug information."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    chat = update.effective_chat
    message_id = update.message.message_id
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    debug_info = f"""🔍 DEBUG INFO - {timestamp}

Chat ID: {chat_id}
Chat Type: {chat.type}
Chat Title: {getattr(chat, 'title', 'Private Chat')}
User ID: {user.id}
Username: @{user.username if user.username else 'no_username'}
First Name: {user.first_name}
Message ID: {message_id}

Test Message: If you see this, messages ARE working!"""
    
    logging.info(f"Sending debug info to chat_id: {chat_id}")
    
    try:
        sent_message = await update.message.reply_text(debug_info)
        logging.info(f"Debug message sent successfully! Message ID: {sent_message.message_id}")
        
        # Send a follow-up
        await asyncio.sleep(1)
        follow_up = await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Follow-up message at {datetime.now().strftime('%H:%M:%S')}"
        )
        logging.info(f"Follow-up sent! Message ID: {follow_up.message_id}")
        
    except Exception as e:
        logging.error(f"Error sending debug message: {e}")

async def get_chat_info():
    """Get information about a specific chat."""
    bot = Bot(token=BOT_TOKEN)
    chat_id = 6186375028  # Your chat ID
    
    try:
        chat = await bot.get_chat(chat_id)
        logging.info(f"Chat info for {chat_id}:")
        logging.info(f"  Type: {chat.type}")
        logging.info(f"  Username: {chat.username}")
        logging.info(f"  First name: {chat.first_name}")
        
        # Try to send a direct message
        test_msg = await bot.send_message(
            chat_id=chat_id,
            text=f"🔔 Direct test message sent at {datetime.now().strftime('%H:%M:%S')}\n\nIf you see this, the bot CAN send you messages!"
        )
        logging.info(f"Direct message sent! Message ID: {test_msg.message_id}")
        
    except Exception as e:
        logging.error(f"Error getting chat info: {e}")

def main():
    """Start the debug bot."""
    # First, try to send a direct message
    asyncio.run(get_chat_info())
    
    # Then start the bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("debug", debug_command))
    
    logging.info("Debug bot started! Send /debug to get debug information")
    application.run_polling()

if __name__ == '__main__':
    main()