# main.py - Production Ready for Render + Real-Time Tracking
import os, asyncio, threading
from flask import Flask, send_from_directory, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

# Flask app MUST be at module level for Gunicorn
app = Flask(__name__, static_folder='.', static_url_path='')

# Firebase Setup (from environment variables - SECURE)
db = None
try:
    if os.getenv("FIREBASE_PRIVATE_KEY"):
        cred = credentials.Certificate({
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
        })
        firebase_admin.initialize_app(cred)
        db = firestore.client()
except Exception as e:
    print(f"⚠️ Firebase init: {e}")

# Flask Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/health')
def health():
    return jsonify({"status": "online", "firebase": "connected" if db else "disconnected"})

# Telegram Bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if db:
        try:
            db.collection('events').add({
                'type': 'TryBot',
                'funnelStep': 'started',  # ✅ Marks actual /start usage
                'telegramUserId': user.id,
                'username': user.username,
                'firstName': user.first_name,
                'language': user.language_code,
                'timestamp': firestore.SERVER_TIMESTAMP,  # ✅ Accurate server time
                'source': 'telegram_bot',
                'country': 'Telegram',  # Bot events
                'countryCode': 'TG'
            })
        except Exception as e:
            print(f"Firestore error: {e}")
    await update.message.reply_text(f"👋 Welcome {user.first_name}!\n✅ Bot activated!")

async def bot_main():
    if not BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not set. Bot disabled.")
        return
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", bot_start))
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        print("🤖 Bot listening for /start commands...")
        await asyncio.Event().wait()  # Keep running
    except Exception as e:
        print(f"Bot error: {e}")

def run_bot():
    try:
        asyncio.run(bot_main())
    except Exception as e:
        print(f"Bot thread error: {e}")

# Start bot in background thread (only on Render)
if os.getenv("RENDER") or os.getenv("PORT"):
    threading.Thread(target=run_bot, daemon=True).start()

# Gunicorn entry point (DO NOT CHANGE)
# For local dev only:
if __name__ == '__main__' and not os.getenv("RENDER"):
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
