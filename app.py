# app.py - Production Ready for Render + Gunicorn
import os
import asyncio
import threading
from flask import Flask, send_from_directory, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

# ========================================
# 🔹 MUST BE AT MODULE LEVEL: Flask app named 'app'
# ========================================
app = Flask(__name__, static_folder='.', static_url_path='')

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

db = None
try:
    if all([os.getenv("FIREBASE_PRIVATE_KEY_ID"), os.getenv("FIREBASE_CLIENT_EMAIL")]):
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase connected")
except Exception as e:
    print(f"⚠️ Firebase init skipped: {e}")

# ========================================
# 🔹 Flask Routes
# ========================================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/health')
def health():
    return jsonify({
        "status": "online", 
        "firebase": "connected" if db else "disconnected",
        "bot": "running" if BOT_TOKEN else "disabled"
    })

# ========================================
# 🔹 Telegram Bot
# ========================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if db:
        try:
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
        except Exception as e:
            print(f"Firestore error: {e}")
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        f"✅ Bot activated!\n"
        f"🔗 Channel: https://t.me/+xkwOcW5ZSxIwOGU1"
    )

async def bot_main():
    if not BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not set. Bot disabled.")
        return
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", bot_start))
    print("🤖 Bot started...")
    await app_bot.start()
    await app_bot.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await asyncio.Event().wait()

def run_bot():
    try:
        asyncio.run(bot_main())
    except Exception as e:
        print(f"Bot error: {e}")

# ========================================
# 🔹 Start Bot in Background Thread
# ========================================
if os.getenv("RENDER") or os.getenv("PORT"):  # Running on Render
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("🤖 Bot thread started")

# ========================================
# 🔹 Gunicorn Entry Point (DO NOT CHANGE)
# ========================================
# Gunicorn looks for: app.py → variable named 'app'
# This is already defined at the TOP of this file ✅

# For local development only:
if __name__ == '__main__' and not os.getenv("RENDER"):
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
