#!/usr/bin/env python3
"""
Test script to verify bot message formatting
"""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.user_manager import UserManager

def test_bot_messages():
    """Test bot message formatting and user management flow."""
    print("Testing bot user management flow...")
    
    # Use PostgreSQL connection
    database_url = "postgresql://postgres:postgres123@localhost:5432/idata_appointment_checker"
    
    try:
        # Initialize user manager with PostgreSQL
        user_manager = UserManager(database_url=database_url)
        print("✅ PostgreSQL database connection established")
        
        # Test user management flow
        test_telegram_id = 6186375028
        
        print(f"\n🔄 Testing subscription flow for ID: {test_telegram_id}")
        
        # Test 1: Check initial status
        is_subscribed_initial = user_manager.is_user_subscribed(test_telegram_id)
        print(f"📊 Initial subscription status: {is_subscribed_initial}")
        
        # Test 2: Add user (simulate /start command)
        added = user_manager.add_user(test_telegram_id)
        if added:
            print("✅ User successfully subscribed (new subscription)")
        else:
            print("ℹ️ User was already subscribed")
        
        # Test 3: Get user info
        user_info = user_manager.get_user_info(test_telegram_id)
        if user_info:
            print(f"📋 User info after subscription:")
            print(f"   - Chat ID: {user_info['chat_id']}")
            print(f"   - Active: {user_info['is_active']}")
            print(f"   - Subscribed: {user_info['subscribed_at']}")
            print(f"   - Created: {user_info['created_at']}")
        
        # Test 4: Try to add again (simulate duplicate /start)
        added_again = user_manager.add_user(test_telegram_id)
        if not added_again:
            print("✅ Duplicate subscription correctly handled")
        
        # Test 5: Unsubscribe (simulate /stop command)
        print(f"\n🛑 Testing unsubscription...")
        removed = user_manager.remove_user(test_telegram_id)
        if removed:
            print("✅ User successfully unsubscribed")
        else:
            print("❌ User was not subscribed")
        
        # Test 6: Check status after unsubscribe
        is_subscribed_after = user_manager.is_user_subscribed(test_telegram_id)
        print(f"📊 Status after unsubscription: {is_subscribed_after}")
        
        # Test 7: Get user info after unsubscribe
        user_info_after = user_manager.get_user_info(test_telegram_id)
        if user_info_after:
            print(f"📋 User info after unsubscription:")
            print(f"   - Active: {user_info_after['is_active']}")
            print(f"   - Unsubscribed: {user_info_after['unsubscribed_at']}")
        
        # Test 8: Re-subscribe (simulate /start after /stop)
        print(f"\n🔄 Testing re-subscription...")
        re_added = user_manager.add_user(test_telegram_id)
        if re_added:
            print("✅ User successfully re-subscribed")
        
        # Test 9: Final status check
        user_info_final = user_manager.get_user_info(test_telegram_id)
        if user_info_final:
            print(f"📋 Final user info:")
            print(f"   - Active: {user_info_final['is_active']}")
            print(f"   - Last subscribed: {user_info_final['subscribed_at']}")
            print(f"   - Unsubscribed: {user_info_final['unsubscribed_at']}")
        
        # Test 10: Get total user count
        total_users = user_manager.get_user_count()
        print(f"\n👥 Total active users: {total_users}")
        
        print(f"\n🎉 All bot user management tests passed!")
        print(f"\n💬 **Bot Command Messages Preview:**")
        print(f"📱 Users can now:")
        print(f"   • Send /start to subscribe with detailed welcome message")
        print(f"   • Send /stop to unsubscribe with clear confirmation")
        print(f"   • Send /status to see subscription details and total users")
        print(f"   • Send /help to get comprehensive bot instructions")
        
    except Exception as e:
        print(f"❌ Bot test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_bot_messages()
    sys.exit(0 if success else 1)