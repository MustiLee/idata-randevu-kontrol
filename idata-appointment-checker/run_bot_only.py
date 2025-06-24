#!/usr/bin/env python3
"""
Run only the Telegram bot for testing commands
"""

import asyncio
import logging
import sys
from src.config import load_config
from src.bot.bot_handler import BotHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Run the Telegram bot."""
    try:
        # Load configuration
        config = load_config()
        
        # Build database URL if database is enabled
        database_url = None
        if config['database']['enabled']:
            if config['database']['url']:
                database_url = config['database']['url']
            else:
                database_url = (
                    f"postgresql://{config['database']['user']}:{config['database']['password']}"
                    f"@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}"
                )
        
        # Initialize bot
        bot_handler = BotHandler(
            token=config['telegram']['bot_token'],
            database_url=database_url,
            users_file="users.json"
        )
        
        # Add existing chat_id if available
        if config['telegram']['chat_id'] and config['telegram']['chat_id'] != 0:
            existing_chat_id = config['telegram']['chat_id']
            if bot_handler.user_manager.add_user(existing_chat_id):
                logging.info(f"Added existing Telegram ID {existing_chat_id} to database")
            else:
                logging.info(f"Existing Telegram ID {existing_chat_id} already in database")
        
        # Setup handlers
        bot_handler.setup_handlers()
        
        logging.info("Starting Telegram bot...")
        logging.info("Bot commands available: /start, /stop, /status, /help")
        logging.info("Press Ctrl+C to stop")
        
        # Start polling
        await bot_handler.start_polling()
        
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())