const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static('public'));

// API endpoints
app.get('/api/users', (req, res) => {
    res.json([
        { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active', role: 'Admin', gifts: 3 },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'active', role: 'User', gifts: 1 },
        { id: 3, name: 'Robert Johnson', email: 'robert@example.com', status: 'active', role: 'Moderator', gifts: 2 }
    ]);
});

app.get('/api/stats', (req, res) => {
    res.json({
        monthlyUsers: 106,
        activeUsers: 9,
        photosToday: 87,
        totalMessages: 88
    });
});

app.post('/api/notify', express.json(), (req, res) => {
    console.log('🎁 Gift notification:', req.body);
    res.json({ success: true });
});

// All routes go to index.html
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`✅ HCO-Cam running on http://localhost:${PORT}`);
});
