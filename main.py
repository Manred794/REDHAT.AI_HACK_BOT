# bot_tracker.py - Telegram Bot for /start tracking
# Install: pip install python-telegram-bot firebase-admin

import os
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# 🔹 Firebase Setup (Service Account - SERVER SIDE ONLY)
cred = credentials.Certificate('firebase-key.json')  # ⚠️ এই ফাইল সার্ভারে রাখুন, পাবলিক করবেন না!
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔹 Bot Token
BOT_TOKEN = "7800960438:AAHClKT7aYbZxSyRMNATYJDLenrsI-BOLrM"  # @BotFather থেকে নিন

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = user.id
    
    # Track /start command in Firestore
    db.collection('events').add({
        'type': 'TryBot',
        'funnelStep': 'started',  # ✅ This marks actual /start usage
        'telegramUserId': chat_id,
        'username': user.username,
        'firstName': user.first_name,
        'language': user.language_code,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'source': 'telegram_bot'
    })
    
    # Send welcome message
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "✅ Bot activated successfully!\n"
        "🎯 You'll now receive Aviator prediction signals.\n\n"
        "🔗 Join our channel: https://t.me/+xkwOcW5ZSxIwOGU1"
    )

async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Optional: Track other bot interactions
    db.collection('events').add({
        'type': 'BotInteraction',
        'telegramUserId': update.effective_user.id,
        'message': update.message.text[:100] if update.message.text else '',
        'timestamp': firestore.SERVER_TIMESTAMP
    })

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_message))
    
    print("🤖 Bot started. Listening for /start commands...")
    app.run_polling()

if __name__ == "__main__":
    main()
