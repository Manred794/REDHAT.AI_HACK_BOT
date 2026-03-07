# main.py - COMPLETE ALL-IN-ONE (HARDCODED CREDENTIALS - NOT SECURE)
import os, asyncio, threading
from flask import Flask, send_from_directory, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__, static_folder='.', static_url_path='')

# 🔴 HARD-CODED FIREBASE CONFIG (FROM YOUR JSON)
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "bynex-ai",
    "private_key_id": "bed195ea950dced0380445e856d0e133c2d8c980",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC9fGP+914gjvQe\nVnctqLlcJ2RZnJ2sUErGLXp4bc3EF5zmvroLQdouPTlftXEGF0R8odem8zZwGmfQ\n878TIFSiUVkR588YuQlwuWUBrdJejjNuQ0dFnow6FC+hhfGdqu2cPm62cESO27W+\nNB9+ZwxcTuUhh5xtRvYyymT0qUky5klXguCA/tbL3LBYyw2/ktPlXL9xRSYxOs4R\nrXTRUhrN/5BrYA3vKG/xfkWbUaE4xPayUaTkuKO5Tv1kf8UCGPt+zsNy0yu/wDDr\nbVsWXkD9pzDdnjsUjRswRl4HdkMH2MwErOsdYn3TEbaVTQmb2KBtjl2XnZ1Dbbem\ndKoRglc5AgMBAAECggEABb3Qp0edHeK5SZyc9Nm4S4qcl7rPNR01/s9oG4Wgy2wS\n4qYkGW0UdbLuNwuyCNAkGeU9Oe0ohnjpyIeNokBfCUahTzY52m5rwJfcXW4or74Q\nTnRbR5HTyA1OY08LMKoxAakLe+Sv9x2cdGEFgmrro772z/h9vx9XrtdMaatrMQaC\n8MUpMBxrenrrgEe7p3J4YBczCV/EkFgW92B3XtIbGsKOFfvmp7rMETZHROzyKQAw\nd9rcTwFs4jub9y23lOUBJCmhlpLHV2ysu4qMsOPp9YZmiq1IFYssQwvFfVxXaJ54\ni7BI7pPkiBVDu+fdzuG2zJGe7rT7BpqX/YzQes9kBwKBgQDmYB0SkkD8HUhlEb1r\nV3lpVXdcqP8Sf+K9RqHhrXH/ZMsPdkfSrlHa6GRWTWUPNjVSlB87BxJMjs+ZNCwS\n3Frb3RGIhMcsdISp9q8/dU+Y5F28Njl5ic/9Rt+1i1vQBSvO/gDMIxIXBBbsVbBh\nBwajGsFJ7SPdHs6KIY1GRJG95wKBgQDSj/T7Ak34lcHxKGC6uJBWNDMIQ7ML+JGf\nnkPEzz62riLjxEPEzvcdGKMfWsm5a1DTeHXaO8r8QnoZQFgg3OTXALce0XQuhlHy\nkr+R2mJCgu73X8j0aagxahB2vi95Ur+MrGXIGyCfwXqbPurmycrzEzD1h+s42l56\nMlJESsdd3wKBgEwlbLacvPoYO7ucd32pdioI4+EuwtC8kJd7ZzqO9+UwzaWYtPjA\nQbIXqkKUZlj20/0tlH0QQ04mzhuXkRHS3/1YPtle+e6JvOfo79gL0Hl60jjJu4me\nsa7H5F2/aGODsg1DC8Rtuyb8ZQ9M63XGurzitQzYY0hNTHt/x5B4Tav1AoGAV6DF\naTjaThu07LHLH6nzl4x9uHDEMLUvlWf9+Afvp4LszjE9qsgfGyLHsCLOVLYOmxNE\nqJ+9qCHaQmv+wR5stfV8P/0XBs2riPH9e6uQvPFUleps7RqTfo0PcPtRMoJ3aQnO\nCesQNqwEZFtY0tcj+OkBtQztnWlzbBNJHVapha0CgYEAkm+nYjeB0/8aQWOCJMSV\nf6VEbyUjdzdaMWc6qVtWItJmZvWEbLirRtARurZ/IHDn7UhOXKsWtNaL8Eh/8Or7\nWdlvs3Va1ClWb2wI2AcrytGbQW8gkRk/9/YaoB621f93cU1HJ5NMLB/n/PiGySzh\nPJXTKpgxo0hDpgxUW9mugEM=\n-----END PRIVATE KEY-----",
    "client_email": "firebase-adminsdk-fbsvc@bynex-ai.iam.gserviceaccount.com",
    "client_id": "107878961002584724516",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40bynex-ai.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔴 HARD-CODED BOT TOKEN
BOT_TOKEN = "7800960438:AAHClKT7aYbZxSyRMNATYJDLenrsI-BOLrM"

# Flask Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/health')
def health():
    return jsonify({"status": "online", "firebase": "connected"})

# Telegram Bot Handler
async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.collection('events').add({
        'type': 'TryBot', 'funnelStep': 'started',
        'telegramUserId': user.id, 'username': user.username,
        'firstName': user.first_name, 'timestamp': firestore.SERVER_TIMESTAMP,
        'source': 'telegram_bot'
    })
    await update.message.reply_text(f"👋 Welcome {user.first_name}!\n✅ Bot activated!")

async def bot_main():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", bot_start))
    await app_bot.start()
    await app_bot.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await asyncio.Event().wait()

def run_bot():
    asyncio.run(bot_main())

# Start bot in background thread
threading.Thread(target=run_bot, daemon=True).start()

# Gunicorn entry point (DO NOT CHANGE)
# For local dev only:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
