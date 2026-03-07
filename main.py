import os
import threading
from flask import Flask, send_from_directory, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

# Flask
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/admin")
def admin():
    return send_from_directory(".", "admin.html")

@app.route("/health")
def health():
    return jsonify({"status": "online"})

# Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "7800960438:AAHClKT7aYbZxSyRMNATYJDLenrsI-BOLrM")

async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.collection("events").add({
        "type": "TryBot",
        "telegramUserId": user.id,
        "username": user.username,
        "firstName": user.first_name,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    await update.message.reply_text(f"👋 Welcome {user.first_name}! Bot activated!")

def start_telegram_bot():
    """Run the bot in a separate thread"""
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", bot_start))
    print("Telegram bot started...")
    app_bot.run_polling()  # blocking, but in a separate thread

if __name__ == "__main__":
    # Start Telegram bot in a thread
    threading.Thread(target=start_telegram_bot, daemon=True).start()

    # Start Flask normally
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
