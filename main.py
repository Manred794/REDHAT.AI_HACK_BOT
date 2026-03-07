import os
import asyncio
import threading

from flask import Flask, send_from_directory, jsonify

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import firebase_admin
from firebase_admin import credentials, firestore


# -------------------------
# Flask Setup
# -------------------------

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


# -------------------------
# Firebase Setup
# -------------------------

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


# -------------------------
# Telegram Bot
# -------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")


async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    db.collection("events").add({
        "type": "TryBot",
        "funnelStep": "started",
        "telegramUserId": user.id,
        "username": user.username,
        "firstName": user.first_name,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "source": "telegram_bot"
    })

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n✅ Bot activated!"
    )


async def bot_main():

    bot = Application.builder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler("start", bot_start))

    print("Telegram bot started")

    await bot.run_polling()


def run_bot():
    asyncio.run(bot_main())


# -------------------------
# Run bot in background
# -------------------------

threading.Thread(target=run_bot, daemon=True).start()


# -------------------------
# Local run (dev only)
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
