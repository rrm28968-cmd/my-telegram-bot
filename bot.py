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

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- AAPKI DETAILS ---
ADMIN_ID = 7757393559  # Aapki User ID Yahan Set Ho Gayi Hai
VIDEO_LINK = "https://t.me/+L9-IXAw3cixHWM1"  # Aapka Video Link
UPI_ID = "9337091479@fam"
PRICE = "149"


# Render Web Server for Health Check
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
            f"👉 Kisi bhi UPI app se payment karein aur **Screenshot** yahan bhej dein."
        )
        await query.edit_message_text(pay_text, parse_mode="Markdown")

    # Admin Approve/Reject Logic
    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 **Payment Verified!**\n\nAapka video access link ye raha:\n{VIDEO_LINK}",
                parse_mode="Markdown"
            )
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n✅ **STATUS: APPROVED**"
            )
        except Exception as e:
            await query.edit_message_caption(caption=f"Error sending link: {e}")

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ **Payment Verification Failed!**\n\nAapka screenshot galat ya incomplete hai. Kripya sahi payment screenshot bhejein."
            )
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n❌ **STATUS: REJECTED**"
            )
        except Exception as e:
            await query.edit_message_caption(caption=f"Error: {e}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id

    # User ko notification
    await update.message.reply_text(
        "⏳ **Payment screenshot mil gaya!**\n\nAdmin ise verify kar rahe hain, kripya thoda wait karein...",
        parse_mode="Markdown"
    )

    # Admin ko screenshot bhejna
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(admin_keyboard)

    username_str = f"@{user.username}" if user.username else "No Username"
    caption_text = (
        f"📩 **New Payment Screenshot!**\n\n"
        f"• **User:** {user.first_name} ({username_str})\n"
        f"• **User ID:** `{user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=caption_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


if __name__ == "__main__":
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
