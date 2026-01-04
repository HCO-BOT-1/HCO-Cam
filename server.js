const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Basic logging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// API Endpoints
app.get('/api/users', (req, res) => {
    res.json({
        success: true,
        users: [
            { id: 1, name: 'John Doe', email: 'john@hco.com', role: 'Admin', gifts: 3 },
            { id: 2, name: 'Jane Smith', email: 'jane@hco.com', role: 'User', gifts: 1 }
        ],
        count: 106
    });
});

app.get('/api/stats', (req, res) => {
    res.json({
        success: true,
        statistics: {
            totalUsers: 106,
            activeUsers: 9,
            photosToday: 0,
            totalGifts: 0,
            onlineUsers: Math.floor(Math.random() * 5) + 6
        }
    });
});

app.post('/api/gift/unlock', (req, res) => {
    try {
        const { userId, userName } = req.body;
        
        console.log(`🎁 Gift unlock request from: ${userName || 'Anonymous'}`);
        
        res.json({
            success: true,
            message: '🎁 Gift unlocked successfully! 8 photos captured (4 front, 4 back)',
            gift: {
                id: Date.now(),
                userId: userId || 'anonymous',
                userName: userName || 'Anonymous User',
                photos: 8,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Failed to unlock gift',
            error: error.message
        });
    }
});

app.post('/api/broadcast', (req, res) => {
    const { message } = req.body;
    
    if (!message) {
        return res.status(400).json({
            success: false,
            message: 'Message is required'
        });
    }
    
    res.json({
        success: true,
        message: `Broadcast sent to all users`,
        data: {
            message: message,
            timestamp: new Date().toISOString()
        }
    });
});

// Serve React/Vue/Angular if you have build folder
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        success: false,
        message: 'Internal server error'
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`🌐 URL: http://0.0.0.0:${PORT}`);
    console.log(`🎁 Surprise Gift System: READY`);
});
