#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database setup
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.user_manager import UserManager

def test_postgres_setup():
    """Test PostgreSQL database setup."""
    print("Testing PostgreSQL database setup...")
    
    # Use PostgreSQL connection
    database_url = "postgresql://postgres:postgres123@localhost:5432/idata_appointment_checker"
    
    try:
        # Initialize user manager with PostgreSQL
        user_manager = UserManager(database_url=database_url)
        print("✅ PostgreSQL database connection established")
        
        # Test adding your Telegram ID
        your_telegram_id = 6186375028
        
        if user_manager.add_user(your_telegram_id):
            print(f"✅ Added your Telegram ID {your_telegram_id} to PostgreSQL")
        else:
            print(f"ℹ️ Your Telegram ID {your_telegram_id} was already in PostgreSQL")
        
        # Test getting user info
        user_info = user_manager.get_user_info(your_telegram_id)
        if user_info:
            print(f"✅ User info retrieved from PostgreSQL:")
            print(f"   - Chat ID: {user_info['chat_id']}")
            print(f"   - Active: {user_info['is_active']}")
            print(f"   - Subscribed: {user_info['subscribed_at']}")
            print(f"   - Created: {user_info['created_at']}")
        
        # Test getting all users
        all_users = user_manager.get_all_users()
        print(f"✅ Total active users in PostgreSQL: {len(all_users)}")
        print(f"   - User IDs: {all_users}")
        
        # Test subscription check
        is_subscribed = user_manager.is_user_subscribed(your_telegram_id)
        print(f"✅ Is {your_telegram_id} subscribed? {is_subscribed}")
        
        print(f"\n🎉 PostgreSQL database tests passed!")
        print(f"📊 Your Telegram ID {your_telegram_id} is now stored in PostgreSQL database")
        
    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_postgres_setup()
    sys.exit(0 if success else 1)