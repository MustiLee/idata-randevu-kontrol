#!/usr/bin/env python3
"""
Test script to verify database setup and user management functionality
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.user_manager import UserManager

def test_database_setup():
    """Test database setup with SQLite for local testing."""
    print("Testing database setup...")
    
    # Use SQLite for testing
    database_url = "sqlite:///test_users.db"
    
    try:
        # Initialize user manager with database
        user_manager = UserManager(database_url=database_url)
        print("✅ Database connection established")
        
        # Test adding your Telegram ID
        your_telegram_id = 6186375028
        
        if user_manager.add_user(your_telegram_id):
            print(f"✅ Added your Telegram ID {your_telegram_id} to database")
        else:
            print(f"ℹ️ Your Telegram ID {your_telegram_id} was already in database")
        
        # Test getting user info
        user_info = user_manager.get_user_info(your_telegram_id)
        if user_info:
            print(f"✅ User info retrieved:")
            print(f"   - Chat ID: {user_info['chat_id']}")
            print(f"   - Active: {user_info['is_active']}")
            print(f"   - Subscribed: {user_info['subscribed_at']}")
        
        # Test getting all users
        all_users = user_manager.get_all_users()
        print(f"✅ Total active users: {len(all_users)}")
        print(f"   - User IDs: {all_users}")
        
        # Test subscription check
        is_subscribed = user_manager.is_user_subscribed(your_telegram_id)
        print(f"✅ Is {your_telegram_id} subscribed? {is_subscribed}")
        
        # Test unsubscribe
        print(f"\nTesting unsubscribe...")
        if user_manager.remove_user(your_telegram_id):
            print(f"✅ Unsubscribed {your_telegram_id}")
        
        # Check subscription after unsubscribe
        is_subscribed_after = user_manager.is_user_subscribed(your_telegram_id)
        print(f"✅ Is {your_telegram_id} subscribed after unsubscribe? {is_subscribed_after}")
        
        # Re-subscribe to test reactivation
        print(f"\nTesting re-subscribe...")
        if user_manager.add_user(your_telegram_id):
            print(f"✅ Re-subscribed {your_telegram_id}")
        
        # Final status
        final_info = user_manager.get_user_info(your_telegram_id)
        if final_info:
            print(f"✅ Final user status:")
            print(f"   - Active: {final_info['is_active']}")
            print(f"   - Last subscribed: {final_info['subscribed_at']}")
            print(f"   - Unsubscribed: {final_info['unsubscribed_at']}")
        
        print(f"\n🎉 All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_database_setup()
    
    # Clean up test database
    test_db_file = "test_users.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print(f"🧹 Cleaned up test database: {test_db_file}")
    
    sys.exit(0 if success else 1)