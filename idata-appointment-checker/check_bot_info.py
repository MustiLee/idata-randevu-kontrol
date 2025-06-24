#!/usr/bin/env python3
"""
Check bot information
"""

import asyncio
from telegram import Bot

BOT_TOKEN = "7548481068:AAGu39H2aOC5W0ml6Cnoc0rFuLMR4406BCw"

async def check_bot():
    bot = Bot(token=BOT_TOKEN)
    
    # Get bot info
    bot_info = await bot.get_me()
    print(f"Bot Username: @{bot_info.username}")
    print(f"Bot Name: {bot_info.first_name}")
    print(f"Bot ID: {bot_info.id}")
    print(f"Can Join Groups: {bot_info.can_join_groups}")
    print(f"Can Read Messages: {bot_info.can_read_all_group_messages}")
    
    # Send a test message with current time
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    try:
        msg = await bot.send_message(
            chat_id=6186375028,
            text=f"🤖 Test from @{bot_info.username}\n\n"
                 f"Time: {now}\n"
                 f"Bot Name: {bot_info.first_name}\n\n"
                 f"If you see this message, please:\n"
                 f"1. Check your Telegram app\n"
                 f"2. Look for messages from @{bot_info.username}\n"
                 f"3. Make sure the bot isn't muted"
        )
        print(f"\n✅ Message sent successfully!")
        print(f"Message ID: {msg.message_id}")
        print(f"Date: {msg.date}")
        print(f"\nPlease check your Telegram for messages from @{bot_info.username}")
    except Exception as e:
        print(f"\n❌ Error sending message: {e}")

if __name__ == "__main__":
    asyncio.run(check_bot())