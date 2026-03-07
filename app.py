# main.py - Complete All-in-One Solution
import os
import asyncio
import threading
from flask import Flask, send_from_directory, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

# ========================================
# 🔹 Firebase Setup (From Environment Variables)
# ========================================
firebase_config = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID", "bynex-ai"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_URL"),
    "universe_domain": "googleapis.com"
}

try:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected")
except Exception as e:
    print(f"⚠️ Firebase error: {e}")
    db = None

# ========================================
# 🔹 Flask Web Server
# ========================================
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/health')
def health():
    return jsonify({"status": "online", "firebase": "connected" if db else "disconnected"})

# ========================================
# 🔹 Telegram Bot
# ========================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if db:
        db.collection('events').add({
            'type': 'TryBot',
            'funnelStep': 'started',
            'telegramUserId': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'language': user.language_code,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'source': 'telegram_bot'
        })
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        f"✅ Bot activated successfully!\n"
        f"🎯 You'll now receive Aviator prediction signals.\n\n"
        f"🔗 Join channel: https://t.me/+xkwOcW5ZSxIwOGU1"
    )

async def bot_main():
    if not BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not set. Bot disabled.")
        return
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", bot_start))
    print("🤖 Bot started. Listening for /start commands...")
    await app_bot.start()
    await app_bot.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await asyncio.Event().wait()  # Keep running

def run_bot():
    asyncio.run(bot_main())

# ========================================
# 🔹 Start Both Web + Bot
# ========================================
if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start web server
    port = int(os.getenv("PORT", 8080))
    print(f"🌐 Web server running on port {port}")
    print(f"📊 Admin panel: https://your-app.onrender.com/admin")
    app.run(host='0.0.0.0', port=port)
