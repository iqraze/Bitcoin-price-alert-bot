import asyncio
import requests
from flask import Flask
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = " PASTE YOUR TELEGRAM BOT TOKEN "   

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 🚀"

# Flask run karne ka thread
def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# ---------------- PRICE SYSTEM --------------------
users = set()
last_level = None

def get_price():
    # Binance API — super stable
    r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
    data = r.json()
    return float(data["price"])   # Binance always returns "price"

async def check_price(app):
    global last_level
    print("Background price task running...")

    while True:
        try:
            price = get_price()
            lvl = int(price // 1000 * 1000)

            if last_level is None:
                last_level = lvl

            if lvl != last_level:
                direction = "UPWARD 🚀" if lvl > last_level else "DOWNWARD 📉"
                msg = f"Bitcoin moved {direction}\nHit Level: ${lvl:,}"

                for uid in list(users):
                    try:
                        await app.bot.send_message(uid, msg)
                    except Exception as e:
                        print("Send error:", e)

                last_level = lvl

        except Exception as e:
            print("Price error:", e)

        await asyncio.sleep(1)

# ---------------- TELEGRAM BOT --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text("BTC Alerts ON 🔔 (I will notify every $1000 move)")

print("BOT STARTING...")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Background price checker start
async def on_start(app):
    asyncio.create_task(check_price(app))

application.post_init = on_start

print("BOT RUNNING...")
application.run_polling()
