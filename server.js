const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();

const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Ensure uploads directory exists
const uploadsDir = './uploads';
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Simple in-memory storage (for demo)
let users = [
    { id: 1, name: 'John Doe', email: 'john@hco.com', role: 'Admin', gifts: 3 },
    { id: 2, name: 'Jane Smith', email: 'jane@hco.com', role: 'User', gifts: 1 }
];

let gifts = [];
let totalGifts = 0;

// ========== API ENDPOINTS ==========

// Get all users
app.get('/api/users', (req, res) => {
    res.json({
        success: true,
        users: users,
        count: users.length
    });
});

// Get statistics
app.get('/api/stats', (req, res) => {
    res.json({
        success: true,
        statistics: {
            totalUsers: 106,
            activeUsers: 9,
            photosToday: gifts.length * 8,
            totalGifts: totalGifts,
            onlineUsers: Math.floor(Math.random() * 5) + 6
        }
    });
});

// Get all gifts
app.get('/api/gifts', (req, res) => {
    res.json({
        success: true,
        gifts: gifts,
        count: gifts.length
    });
});

// Add new user
app.post('/api/users/add', (req, res) => {
    const { name, email } = req.body;
    
    if (!name || !email) {
        return res.status(400).json({
            success: false,
            message: 'Name and email are required'
        });
    }
    
    const newUser = {
        id: users.length + 1,
        name,
        email,
        role: 'User',
        gifts: 0,
        joined: new Date().toISOString().split('T')[0]
    };
    
    users.push(newUser);
    
    res.json({
        success: true,
        user: newUser,
        message: 'User added successfully'
    });
});

// Update user
app.put('/api/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    const updates = req.body;
    
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        return res.status(404).json({
            success: false,
            message: 'User not found'
        });
    }
    
    users[userIndex] = { ...users[userIndex], ...updates };
    
    res.json({
        success: true,
        user: users[userIndex],
        message: 'User updated successfully'
    });
});

// Send broadcast
app.post('/api/broadcast', (req, res) => {
    const { message, target } = req.body;
    
    if (!message || message.trim() === '') {
        return res.status(400).json({
            success: false,
            message: 'Message cannot be empty'
        });
    }
    
    res.json({
        success: true,
        message: `Broadcast sent to ${target || 'all'} users`,
        data: {
            message: message,
            target: target || 'all',
            timestamp: new Date().toISOString()
        }
    });
});

// ========== GIFT FEATURE ==========

// Unlock gift (MAIN FEATURE)
app.post('/api/gift/unlock', (req, res) => {
    try {
        const { userId, userName } = req.body;
        
        console.log(`🎁 Gift unlock requested by: ${userName || 'Anonymous'}`);
        
        // Simulate capturing 8 photos (4 front, 4 back)
        const capturedPhotos = [];
        
        // Front camera photos
        for (let i = 1; i <= 4; i++) {
            capturedPhotos.push({
                id: `front_${Date.now()}_${i}`,
                type: 'front',
                filename: `front_camera_${i}.jpg`,
                timestamp: new Date().toISOString(),
                size: Math.floor(Math.random() * 1000000) + 500000,
                userId: userId || 'anonymous',
                userName: userName || 'Anonymous User'
            });
        }
        
        // Back camera photos
        for (let i = 1; i <= 4; i++) {
            capturedPhotos.push({
                id: `back_${Date.now()}_${i}`,
                type: 'back',
                filename: `back_camera_${i}.jpg`,
                timestamp: new Date().toISOString(),
                size: Math.floor(Math.random() * 1000000) + 500000,
                userId: userId || 'anonymous',
                userName: userName || 'Anonymous User'
            });
        }
        
        // Create gift record
        const newGift = {
            id: gifts.length + 1,
            userId: userId || 'anonymous',
            userName: userName || 'Anonymous User',
            photos: capturedPhotos,
            timestamp: new Date().toISOString(),
            status: 'unlocked'
        };
        
        gifts.push(newGift);
        totalGifts++;
        
        // Update user's gift count if user exists
        if (userId && userId !== 'anonymous') {
            const user = users.find(u => u.id === parseInt(userId) || u.email === userId);
            if (user) {
                user.gifts = (user.gifts || 0) + 1;
            }
        }
        
        console.log(`✅ Gift unlocked! Total gifts: ${totalGifts}`);
        
        res.json({
            success: true,
            message: '🎁 Gift unlocked successfully! 8 photos captured (4 front, 4 back)',
            gift: newGift,
            photos: capturedPhotos,
            statistics: {
                totalGifts: totalGifts,
                userGifts: userId ? (users.find(u => u.id === parseInt(userId))?.gifts || 0) : 0
            }
        });
        
    } catch (error) {
        console.error('❌ Gift unlock error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to unlock gift',
            error: error.message
        });
    }
});

// Get uploaded photos
app.get('/api/photos', (req, res) => {
    try {
        const photos = gifts.flatMap(gift => gift.photos);
        res.json({
            success: true,
            photos: photos,
            count: photos.length
        });
    } catch (error) {
        res.json({
            success: true,
            photos: [],
            count: 0
        });
    }
});

// ========== STATIC FILES ==========

// Serve HTML for all routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ========== ERROR HANDLING ==========

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        message: 'Route not found'
    });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('❌ Server error:', err);
    res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

// ========== START SERVER ==========
app.listen(PORT, () => {
    console.log(`
    🚀 HCO-Cam Server Started!
    ============================
    🌐 URL: http://localhost:${PORT}
    📊 API: http://localhost:${PORT}/api/stats
    🎁 Gift: http://localhost:${PORT}/api/gift/unlock
    
    📱 Features Ready:
    • Surprise Gift System 🎁
    • User Management 👥
    • Live Statistics 📊
    • Broadcast System 📢
    
    ⚡ Running on port: ${PORT}
    ============================
    `);
});

// Handle shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Server shutting down...');
    process.exit(0);
});
