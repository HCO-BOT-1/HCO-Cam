#!/data/data/com.termux/files/usr/bin/bash

# Make sure env vars are set
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
export ADMIN_ID="YOUR_TELEGRAM_ID"
export SERVER_LINK="http://localhost:3000"

# Run server in background
echo "🚀 Starting server..."
node server.js &

# Run bot
echo "🤖 Starting Telegram bot..."
node bot.js
