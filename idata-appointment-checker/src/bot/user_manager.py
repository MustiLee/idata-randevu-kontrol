import json
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database.models import DatabaseManager, TelegramUser

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, database_url: Optional[str] = None, users_file: str = "users.json"):
        self.users_file = users_file
        self.database_url = database_url
        self.db_manager = None
        
        if database_url:
            try:
                self.db_manager = DatabaseManager(database_url)
                self.db_manager.create_tables()
                logger.info("Database connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                logger.info("Falling back to JSON file storage")
                self.db_manager = None
    
    def _migrate_json_to_db(self):
        """Migrate existing users from JSON file to database."""
        if not self.db_manager or not os.path.exists(self.users_file):
            return
            
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                users = data if isinstance(data, list) else []
                
            session = self.db_manager.get_session()
            try:
                for chat_id in users:
                    existing_user = session.query(TelegramUser).filter(
                        TelegramUser.chat_id == chat_id
                    ).first()
                    
                    if not existing_user:
                        user = TelegramUser(
                            chat_id=chat_id,
                            subscribed_at=datetime.now(),
                            is_active=True
                        )
                        session.add(user)
                        logger.info(f"Migrated user {chat_id} from JSON to database")
                
                session.commit()
                logger.info("JSON to database migration completed")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to migrate users: {e}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to read JSON file for migration: {e}")
    
    def add_user(self, chat_id: int) -> bool:
        """Add a user to the database or JSON file."""
        if self.db_manager:
            return self._add_user_db(chat_id)
        else:
            return self._add_user_json(chat_id)
    
    def _add_user_db(self, chat_id: int) -> bool:
        """Add user to database."""
        session = self.db_manager.get_session()
        try:
            existing_user = session.query(TelegramUser).filter(
                TelegramUser.chat_id == chat_id
            ).first()
            
            if existing_user:
                if not existing_user.is_active:
                    # Reactivate user
                    existing_user.is_active = True
                    existing_user.subscribed_at = datetime.now()
                    existing_user.unsubscribed_at = None
                    existing_user.updated_at = datetime.now()
                    session.commit()
                    logger.info(f"Reactivated user {chat_id}")
                    return True
                else:
                    # User already active
                    return False
            else:
                # New user
                user = TelegramUser(
                    chat_id=chat_id,
                    subscribed_at=datetime.now(),
                    is_active=True
                )
                session.add(user)
                session.commit()
                logger.info(f"Added new user {chat_id}")
                return True
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding user {chat_id}: {e}")
            return False
        finally:
            session.close()
    
    def _add_user_json(self, chat_id: int) -> bool:
        """Add user to JSON file (fallback)."""
        users = self._load_users_json()
        if chat_id not in users:
            users.append(chat_id)
            self._save_users_json(users)
            return True
        return False
    
    def remove_user(self, chat_id: int) -> bool:
        """Remove a user from the database or JSON file."""
        if self.db_manager:
            return self._remove_user_db(chat_id)
        else:
            return self._remove_user_json(chat_id)
    
    def _remove_user_db(self, chat_id: int) -> bool:
        """Remove user from database (soft delete)."""
        session = self.db_manager.get_session()
        try:
            user = session.query(TelegramUser).filter(
                TelegramUser.chat_id == chat_id,
                TelegramUser.is_active == True
            ).first()
            
            if user:
                user.is_active = False
                user.unsubscribed_at = datetime.now()
                user.updated_at = datetime.now()
                session.commit()
                logger.info(f"Deactivated user {chat_id}")
                return True
            else:
                return False
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error removing user {chat_id}: {e}")
            return False
        finally:
            session.close()
    
    def _remove_user_json(self, chat_id: int) -> bool:
        """Remove user from JSON file (fallback)."""
        users = self._load_users_json()
        if chat_id in users:
            users.remove(chat_id)
            self._save_users_json(users)
            return True
        return False
    
    def get_all_users(self) -> List[int]:
        """Get all active users."""
        if self.db_manager:
            return self._get_all_users_db()
        else:
            return self._load_users_json()
    
    def _get_all_users_db(self) -> List[int]:
        """Get all active users from database."""
        session = self.db_manager.get_session()
        try:
            users = session.query(TelegramUser).filter(
                TelegramUser.is_active == True
            ).all()
            return [user.chat_id for user in users]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting users: {e}")
            return []
        finally:
            session.close()
    
    def is_user_subscribed(self, chat_id: int) -> bool:
        """Check if user is subscribed."""
        if self.db_manager:
            return self._is_user_subscribed_db(chat_id)
        else:
            return chat_id in self._load_users_json()
    
    def _is_user_subscribed_db(self, chat_id: int) -> bool:
        """Check if user is subscribed in database."""
        session = self.db_manager.get_session()
        try:
            user = session.query(TelegramUser).filter(
                TelegramUser.chat_id == chat_id,
                TelegramUser.is_active == True
            ).first()
            return user is not None
        except SQLAlchemyError as e:
            logger.error(f"Database error checking user {chat_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_user_count(self) -> int:
        """Get total number of active users."""
        if self.db_manager:
            return self._get_user_count_db()
        else:
            return len(self._load_users_json())
    
    def _get_user_count_db(self) -> int:
        """Get user count from database."""
        session = self.db_manager.get_session()
        try:
            count = session.query(TelegramUser).filter(
                TelegramUser.is_active == True
            ).count()
            return count
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user count: {e}")
            return 0
        finally:
            session.close()
    
    def get_user_info(self, chat_id: int) -> Optional[Dict]:
        """Get detailed user information."""
        if not self.db_manager:
            return None
            
        session = self.db_manager.get_session()
        try:
            user = session.query(TelegramUser).filter(
                TelegramUser.chat_id == chat_id
            ).first()
            
            if user:
                return {
                    'chat_id': user.chat_id,
                    'is_active': user.is_active,
                    'subscribed_at': user.subscribed_at,
                    'unsubscribed_at': user.unsubscribed_at,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user info {chat_id}: {e}")
            return None
        finally:
            session.close()
    
    def _load_users_json(self) -> List[int]:
        """Load users from JSON file."""
        try:
            if not os.path.exists(self.users_file):
                return []
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users_json(self, users: List[int]):
        """Save users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)