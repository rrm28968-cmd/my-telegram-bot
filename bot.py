import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Logging Config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Render Environment Variable se Token uthayega (Safe Way)
BOT_TOKEN = os.getenv("BOT_TOKEN")

VIDEO_LINK = "https://t.me/+ggL2fXh9OUs1MDg1"
UPI_ID = "9337091479@fam"
PRICE = "149"


# Render Port Check ke liye Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")


def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"💳 Buy Video (₹{PRICE})", callback_data="buy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 **Welcome!**\n\nVideo khareedne ke liye neeche button par click karein:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        pay_text = (
            f"💰 **Payment Details:**\n\n"
            f"• **Amount:** ₹{PRICE}\n"
            f"• **UPI ID:** `{UPI_ID}`\n\n"
            f"👉 Kisi bhi UPI app (PhonePe/Paytm/GooglePay) se payment karein.\n"
            f"Payment hone ke baad, **Screenshot** yahan chat me bhej dein."
        )
        await query.edit_message_text(pay_text, parse_mode="Markdown")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Payment screenshot mil gaya! Verifying...")
    await update.message.reply_text(
        f"🎉 **Payment Successful!**\n\nAapka video access link ye raha:\n{VIDEO_LINK}",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    # Render Health Check Server Start
    threading.Thread(target=run_health_check_server, daemon=True).start()

    if not BOT_TOKEN:
        print("Error: BOT_TOKEN Environment Variable me nahi mila!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_click))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        print("Bot start ho raha hai...")
        app.run_polling()
