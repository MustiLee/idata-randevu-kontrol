import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from .user_manager import UserManager

logger = logging.getLogger(__name__)

class BotHandler:
    def __init__(self, token: str, database_url: str = None, users_file: str = "users.json"):
        self.token = token
        self.user_manager = UserManager(database_url=database_url, users_file=users_file)
        self.application = None
        
        # Migrate existing JSON users to database if available
        if database_url:
            self.user_manager._migrate_json_to_db()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        user_display_name = user.username or user.first_name or "User"
        
        if self.user_manager.add_user(chat_id):
            message = (
                f"🎉 **Welcome {user_display_name}!**\n\n"
                f"✅ You have been **successfully subscribed** to Italy visa appointment updates.\n\n"
                f"🔔 You will receive instant notifications when appointments become available at:\n"
                f"• Altunizade Office\n"
                f"• Gayrettepe Office\n\n"
                f"📱 **Available Commands:**\n"
                f"• `/status` - Check your subscription status\n"
                f"• `/stop` - Unsubscribe from updates\n\n"
                f"⚡ The bot is now monitoring appointments for you!"
            )
            logger.info(f"New user subscribed: {user_display_name} (ID: {chat_id})")
        else:
            user_info = self.user_manager.get_user_info(chat_id)
            subscription_date = ""
            if user_info and user_info.get('subscribed_at'):
                sub_date = user_info['subscribed_at'].strftime('%Y-%m-%d %H:%M')
                subscription_date = f"\n\n📅 Subscribed since: {sub_date}"
            
            message = (
                f"ℹ️ **Hello {user_display_name}!**\n\n"
                f"You are already subscribed to appointment updates.{subscription_date}\n\n"
                f"📱 **Available Commands:**\n"
                f"• `/status` - Check subscription details\n"
                f"• `/stop` - Unsubscribe from updates\n\n"
                f"⚡ The bot is actively monitoring appointments for you!"
            )
        
        try:
            logger.info(f"Sending message to chat_id {chat_id}: {message[:50]}...")
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"Start command message sent successfully to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send start message to {chat_id}: {e}")
            # Try without markdown
            try:
                await update.message.reply_text(message.replace('*', '').replace('`', ''))
                logger.info(f"Start message sent without markdown to {chat_id}")
            except Exception as e2:
                logger.error(f"Failed to send plain start message to {chat_id}: {e2}")
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        user_display_name = user.username or user.first_name or "User"
        
        if self.user_manager.remove_user(chat_id):
            message = (
                f"👋 **Goodbye {user_display_name}!**\n\n"
                f"❌ You have been **successfully unsubscribed** from Italy visa appointment updates.\n\n"
                f"📭 You will no longer receive notifications about available appointments.\n\n"
                f"💡 **Want to subscribe again?**\n"
                f"Just send `/start` anytime to reactivate your subscription.\n\n"
                f"Thank you for using the IDATA Appointment Checker! 🇮🇹"
            )
            logger.info(f"User unsubscribed: {user_display_name} (ID: {chat_id})")
            logger.info(f"Sending unsubscribe message to chat_id: {chat_id}")
        else:
            message = (
                f"ℹ️ **Hello {user_display_name}!**\n\n"
                f"You are not currently subscribed to appointment updates.\n\n"
                f"💡 **Want to get notified about appointments?**\n"
                f"Send `/start` to subscribe and receive instant notifications when Italy visa appointments become available!"
            )
            logger.info(f"User not subscribed, sending info to chat_id: {chat_id}")
        
        try:
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"Message sent successfully to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            # Try without markdown
            try:
                await update.message.reply_text(message.replace('*', '').replace('`', ''))
                logger.info(f"Message sent without markdown to {chat_id}")
            except Exception as e2:
                logger.error(f"Failed to send plain message to {chat_id}: {e2}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        user_display_name = user.username or user.first_name or "User"
        
        is_subscribed = self.user_manager.is_user_subscribed(chat_id)
        total_users = self.user_manager.get_user_count()
        
        if is_subscribed:
            user_info = self.user_manager.get_user_info(chat_id)
            subscription_details = ""
            if user_info:
                sub_date = user_info['subscribed_at'].strftime('%Y-%m-%d %H:%M')
                subscription_details = f"\n📅 Subscribed since: {sub_date}"
                
                if user_info.get('unsubscribed_at'):
                    unsub_date = user_info['unsubscribed_at'].strftime('%Y-%m-%d %H:%M')
                    subscription_details += f"\n🔄 Last resubscription: {sub_date}"
            
            message = (
                f"📊 **Status Report for {user_display_name}**\n\n"
                f"✅ **Status:** Subscribed to updates\n"
                f"🔔 **Monitoring:** Altunizade & Gayrettepe offices\n"
                f"👥 **Total subscribers:** {total_users}{subscription_details}\n\n"
                f"📱 **Available Commands:**\n"
                f"• `/stop` - Unsubscribe from updates\n\n"
                f"⚡ You will be notified instantly when appointments become available!"
            )
        else:
            message = (
                f"📊 **Status Report for {user_display_name}**\n\n"
                f"❌ **Status:** Not subscribed\n"
                f"👥 **Total subscribers:** {total_users}\n\n"
                f"💡 **Want to get notified?**\n"
                f"Send `/start` to subscribe and receive instant notifications about Italy visa appointments!"
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_display_name = user.username or user.first_name or "User"
        
        message = (
            f"🤖 **IDATA Appointment Checker Bot Help**\n\n"
            f"Hello {user_display_name}! This bot monitors Italy visa appointments at IDATA offices and sends instant notifications when slots become available.\n\n"
            f"🏢 **Monitored Offices:**\n"
            f"• Altunizade Office\n"
            f"• Gayrettepe Office\n\n"
            f"📱 **Available Commands:**\n\n"
            f"`/start` - Subscribe to appointment notifications\n"
            f"`/stop` - Unsubscribe from notifications\n"
            f"`/status` - Check your subscription status\n"
            f"`/help` - Show this help message\n\n"
            f"⚡ **How it works:**\n"
            f"1. Send `/start` to subscribe\n"
            f"2. The bot checks for appointments every 15 minutes\n"
            f"3. You get instant notifications when appointments are found\n"
            f"4. Send `/stop` anytime to unsubscribe\n\n"
            f"🇮🇹 Good luck with your Italy visa application!"
        )
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    def setup_handlers(self):
        if not self.application:
            self.application = Application.builder().token(self.token).build()
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
    
    async def start_polling(self):
        if not self.application:
            self.setup_handlers()
        
        logger.info("Starting Telegram bot polling...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep the polling running
        try:
            # This will run indefinitely until the application is stopped
            import asyncio
            await asyncio.Event().wait()
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
        finally:
            await self.stop_polling()
    
    async def stop_polling(self):
        if self.application:
            logger.info("Stopping Telegram bot polling...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

async def send_message_to_all_users(bot_token: str, message: str, database_url: str = None, users_file: str = "users.json"):
    from telegram import Bot
    
    user_manager = UserManager(database_url=database_url, users_file=users_file)
    bot = Bot(token=bot_token)
    
    users = user_manager.get_all_users()
    failed_users = []
    
    for chat_id in users:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Message sent to user {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send message to user {chat_id}: {e}")
            if "chat not found" in str(e).lower() or "blocked by the user" in str(e).lower():
                failed_users.append(chat_id)
    
    # Remove users who blocked the bot or deleted their account
    for chat_id in failed_users:
        user_manager.remove_user(chat_id)
        logger.info(f"Removed inactive user {chat_id}")
    
    successful_sends = len(users) - len(failed_users)
    logger.info(f"Message sent to {successful_sends}/{len(users)} users")
    
    return successful_sends