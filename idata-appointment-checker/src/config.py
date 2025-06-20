import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv


def load_config() -> Dict:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    # Load .env file if it exists
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    config = {
        'general': {
            'check_interval_minutes': int(os.getenv('CHECK_INTERVAL_MINUTES', '10')),
            'headless_browser': os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        },
        'telegram': {
            'enabled': os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true',
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'chat_id': int(os.getenv('TELEGRAM_CHAT_ID', '0')) if os.getenv('TELEGRAM_CHAT_ID') else 0,
        },
        'email': {
            'enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'smtp_username': os.getenv('EMAIL_SMTP_USERNAME', ''),
            'smtp_password': os.getenv('EMAIL_SMTP_PASSWORD', ''),
            'from_email': os.getenv('EMAIL_FROM', ''),
            'to_email': os.getenv('EMAIL_TO', ''),
        },
        'appointment': {
            'residence_city': os.getenv('RESIDENCE_CITY', 'İstanbul'),
            'idata_offices': os.getenv('IDATA_OFFICES', 'Altunizade,Gayrettepe').split(','),
            'travel_purpose': os.getenv('TRAVEL_PURPOSE', 'Tourism'),
            'service_type': os.getenv('SERVICE_TYPE', 'Standard'),
            'num_persons': os.getenv('NUM_PERSONS', '3'),
        },
        'database': {
            'enabled': os.getenv('DATABASE_ENABLED', 'true').lower() == 'true',
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', '5432')),
            'name': os.getenv('DATABASE_NAME', 'idata_appointment_checker'),
            'user': os.getenv('DATABASE_USER', 'postgres'),
            'password': os.getenv('DATABASE_PASSWORD', ''),
            'url': os.getenv('DATABASE_URL'),  # Alternative to individual components
        }
    }
    
    # Validate required configurations
    if config['telegram']['enabled']:
        if not config['telegram']['bot_token']:
            raise ValueError("Telegram is enabled but BOT_TOKEN is missing")
    
    if config['email']['enabled']:
        required_email_fields = ['smtp_username', 'smtp_password', 'from_email', 'to_email']
        for field in required_email_fields:
            if not config['email'][field]:
                raise ValueError(f"Email is enabled but {field.upper()} is missing")
    
    if config['database']['enabled']:
        if not config['database']['url']:
            # If no URL provided, construct from components
            if not all([config['database']['host'], config['database']['name'], 
                       config['database']['user'], config['database']['password']]):
                raise ValueError("Database is enabled but required connection parameters are missing")
    
    return config