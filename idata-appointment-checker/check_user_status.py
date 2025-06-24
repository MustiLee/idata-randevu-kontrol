#!/usr/bin/env python3
"""
Check user status in database
"""

import sys
from datetime import datetime

sys.path.insert(0, '.')

from src.bot.user_manager import UserManager

def check_user_status():
    """Check user subscription status in database."""
    
    # PostgreSQL connection
    database_url = "postgresql://postgres:postgres123@localhost:5432/idata_appointment_checker"
    
    # Initialize user manager
    user_manager = UserManager(database_url=database_url)
    
    # Your Telegram ID
    your_id = 6186375028
    
    print(f"Checking status for Telegram ID: {your_id}")
    print("=" * 50)
    
    # Check if subscribed
    is_subscribed = user_manager.is_user_subscribed(your_id)
    print(f"Subscription Status: {'✅ ACTIVE' if is_subscribed else '❌ INACTIVE'}")
    
    # Get detailed user info
    user_info = user_manager.get_user_info(your_id)
    if user_info:
        print(f"\nDetailed User Information:")
        print(f"  Chat ID: {user_info['chat_id']}")
        print(f"  Is Active: {user_info['is_active']}")
        print(f"  Subscribed At: {user_info['subscribed_at']}")
        print(f"  Unsubscribed At: {user_info['unsubscribed_at']}")
        print(f"  Created At: {user_info['created_at']}")
        print(f"  Updated At: {user_info['updated_at']}")
    else:
        print("User not found in database")
    
    # Get all active users
    all_users = user_manager.get_all_users()
    print(f"\nTotal Active Users: {len(all_users)}")
    print(f"Active User IDs: {all_users}")
    
    # Check JSON file as well
    print("\n" + "=" * 50)
    print("Checking JSON file (fallback storage):")
    json_users = user_manager._load_users_json()
    print(f"Users in JSON: {json_users}")
    
    return is_subscribed

if __name__ == "__main__":
    check_user_status()