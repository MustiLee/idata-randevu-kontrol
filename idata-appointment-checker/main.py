#!/usr/bin/env python3
"""
IDATA Italy Visa Appointment Checker
Main application entry point
"""

import logging
import sys
from datetime import datetime

from src.config import load_config
from src.notifier.notifier import Notifier
from src.scheduler.scheduler import AppointmentScheduler
from src.scraper.appointment_checker import AppointmentChecker


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
    """
    Main function to check appointments and send notifications.
    
    Args:
        config: Application configuration
    """
    logger = logging.getLogger(__name__)
    
    # Initialize components
    checker = AppointmentChecker(headless=config['general']['headless_browser'])
    notifier = Notifier(config)
    
    try:
        # Check appointments
        is_available, message = checker.check_appointments()
        
        if is_available:
            logger.info(f"APPOINTMENTS AVAILABLE! {message}")
            # Send notification
            notifier.send_appointment_available_notification(message)
        else:
            logger.info(f"No appointments available: {message}")
        
    except Exception as e:
        logger.error(f"Error during appointment check: {e}", exc_info=True)
        # Send error notification
        notifier.send_error_notification(str(e))


def main():
    """Main application entry point."""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     IDATA Italy Visa Appointment Checker      ║
    ║            Turkey Office Edition              ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config['general']['log_level'])
        logger = logging.getLogger(__name__)
        
        logger.info("Starting IDATA Appointment Checker...")
        logger.info(f"Check interval: {config['general']['check_interval_minutes']} minutes")
        logger.info(f"Headless browser: {config['general']['headless_browser']}")
        logger.info(f"Telegram notifications: {config['telegram']['enabled']}")
        logger.info(f"Email notifications: {config['email']['enabled']}")
        
        # Print appointment configuration
        logger.info("Appointment configuration:")
        logger.info(f"  - Residence City: {config['appointment']['residence_city']}")
        logger.info(f"  - IDATA Offices: {', '.join(config['appointment']['idata_offices'])}")
        logger.info(f"  - Travel Purpose: {config['appointment']['travel_purpose']}")
        logger.info(f"  - Service Type: {config['appointment']['service_type']}")
        logger.info(f"  - Number of Persons: {config['appointment']['num_persons']}")
        
        # Initialize notifier for startup notification
        notifier = Notifier(config)
        
        # Create detailed startup message
        startup_message = (
            f"🚀 *IDATA Appointment Checker Started*\n\n"
            f"📅 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⏰ *Check Interval:* Every {config['general']['check_interval_minutes']} minutes\n"
            f"🖥️ *Browser Mode:* {'Headless' if config['general']['headless_browser'] else 'Visible'}\n\n"
            f"*📋 Configuration:*\n"
            f"• City: {config['appointment']['residence_city']}\n"
            f"• Offices: {', '.join(config['appointment']['idata_offices'])}\n"
            f"• Purpose: {config['appointment']['travel_purpose']}\n"
            f"• Service: {config['appointment']['service_type']}\n"
            f"• Persons: {config['appointment']['num_persons']}\n\n"
            f"*🔔 Notifications:*\n"
            f"• Telegram: {'✅ Enabled' if config['telegram']['enabled'] else '❌ Disabled'}\n"
            f"• Email: {'✅ Enabled' if config['email']['enabled'] else '❌ Disabled'}\n\n"
            f"_The bot is now monitoring appointments. You will be notified when slots become available._"
        )
        
        notifier.send_status_notification(startup_message)
        
        # Create scheduler
        scheduler = AppointmentScheduler(
            check_interval_minutes=config['general']['check_interval_minutes']
        )
        
        # Start scheduler with initial check
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