#!/usr/bin/env python3
"""
Run both appointment checker and Telegram bot together
"""

import asyncio
import logging
import sys
import threading
from datetime import datetime
import time

from src.config import load_config
from src.notifier.notifier import Notifier
from src.scheduler.scheduler import AppointmentScheduler
from src.scraper.appointment_checker import AppointmentChecker
from src.bot.bot_handler import BotHandler


def setup_logging(log_level: str = 'INFO'):
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('appointment_checker.log', encoding='utf-8')
        ]
    )


def check_appointments(config: dict):
    """Check appointments and send notifications."""
    logger = logging.getLogger(__name__)
    
    # Initialize components
    checker = AppointmentChecker(headless=config['general']['headless_browser'])
    notifier = Notifier(config)
    
    try:
        # Check appointments
        is_available, message = checker.check_appointments()
        
        if is_available:
            logger.info(f"APPOINTMENTS AVAILABLE! {message}")
            notifier.send_appointment_available_notification(message)
        else:
            logger.info(f"No appointments available: {message}")
        
    except Exception as e:
        logger.error(f"Error during appointment check: {e}", exc_info=True)
        notifier.send_error_notification(str(e))


async def run_telegram_bot(config: dict):
    """Run the Telegram bot in async context."""
    logger = logging.getLogger("TelegramBot")
    
    try:
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
                logger.info(f"Added existing Telegram ID {existing_chat_id} to database")
            else:
                logger.info(f"Existing Telegram ID {existing_chat_id} already in database")
        
        # Setup handlers
        bot_handler.setup_handlers()
        
        logger.info("Telegram bot started and listening for commands")
        logger.info("Bot commands: /start, /stop, /status, /help")
        
        # Start polling
        await bot_handler.start_polling()
        
    except Exception as e:
        logger.error(f"Telegram bot error: {e}", exc_info=True)


def main():
    """Main application entry point."""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     IDATA Italy Visa Appointment Checker      ║
    ║            Turkey Office Edition              ║
    ║         With Enhanced Bot Commands            ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config['general']['log_level'])
        logger = logging.getLogger(__name__)
        
        logger.info("Starting IDATA Appointment Checker with Telegram Bot...")
        logger.info(f"Check interval: {config['general']['check_interval_minutes']} minutes")
        logger.info(f"Telegram bot enabled: {config['telegram']['enabled']}")
        
        # Send startup notification
        notifier = Notifier(config)
        startup_message = (
            f"🚀 *IDATA Appointment Checker Started*\n\n"
            f"📅 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⏰ *Check Interval:* Every {config['general']['check_interval_minutes']} minutes\n\n"
            f"🤖 *Bot Commands Available:*\n"
            f"• `/start` - Subscribe to updates\n"
            f"• `/stop` - Unsubscribe\n"
            f"• `/status` - Check subscription\n"
            f"• `/help` - Get help\n\n"
            f"_The bot is now monitoring appointments and accepting commands._"
        )
        notifier.send_status_notification(startup_message)
        
        # Start Telegram bot in a separate thread
        if config['telegram']['enabled'] and config['telegram']['bot_token']:
            bot_loop = asyncio.new_event_loop()
            
            def run_bot_thread():
                asyncio.set_event_loop(bot_loop)
                bot_loop.run_until_complete(run_telegram_bot(config))
            
            bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
            bot_thread.start()
            logger.info("Telegram bot thread started")
        
        # Give bot time to start
        time.sleep(2)
        
        # Create and start appointment scheduler
        scheduler = AppointmentScheduler(
            check_interval_minutes=config['general']['check_interval_minutes']
        )
        
        scheduler.start(
            check_function=lambda: check_appointments(config),
            initial_check=True
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()