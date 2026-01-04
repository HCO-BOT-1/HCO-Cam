const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from public directory
app.use(express.static('public'));

// API endpoints
app.get('/api/users', (req, res) => {
    res.json([
        { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active', role: 'Admin' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'active', role: 'User' },
        { id: 3, name: 'Robert Johnson', email: 'robert@example.com', status: 'active', role: 'Moderator' },
        { id: 4, name: 'Emily Davis', email: 'emily@example.com', status: 'active', role: 'User' },
        { id: 5, name: 'Michael Wilson', email: 'michael@example.com', status: 'active', role: 'User' }
    ]);
});

app.get('/api/stats', (req, res) => {
    res.json({
        monthlyUsers: 106,
        activeUsers: 9,
        photosToday: 0,
        totalMessages: 88
    });
});

// Handle all routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`✅ HCO-Cam running on http://localhost:${PORT}`);
});
