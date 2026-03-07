import os
import asyncio
import threading
from flask import Flask, send_from_directory, jsonify

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import firebase_admin
from firebase_admin import credentials, firestore


# -----------------------------
# Flask Web Server
# -----------------------------

app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')


@app.route('/health')
def health():
    return jsonify({"status": "online"})


# -----------------------------
# Firebase Setup
# -----------------------------

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "bynex-ai",
    "private_key_id": "bed195ea950dced0380445e856d0e133c2d8c980",
    "private_key": """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@bynex-ai.iam.gserviceaccount.com",
    "client_id": "107878961002584724516",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40bynex-ai.iam.gserviceaccount.com"
})

firebase_admin.initialize_app(cred)
db = firestore.client()


# -----------------------------
# Telegram Bot Setup
# -----------------------------

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"


async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    db.collection('events').add({
        'type': 'TryBot',
        'funnelStep': 'started',
        'telegramUserId': user.id,
        'username': user.username,
        'firstName': user.first_name,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'source': 'telegram_bot'
    })

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n✅ Bot Activated Successfully!"
    )


async def bot_main():

    bot_app = Application.builder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", bot_start))

    print("Telegram bot started...")

    await bot_app.run_polling()


def run_bot():
    asyncio.run(bot_main())


# -----------------------------
# Run Telegram Bot in Background
# -----------------------------

threading.Thread(target=run_bot, daemon=True).start()


# -----------------------------
# Local Development
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
