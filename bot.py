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
ADMIN_ID =  7757393559 # Aapki Admin Telegram ID
VIDEO_LINK = "https://t.me/+ggL2fXh9OUs1MDg1"  # Aapka Link
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
        f"👋 <b>Welcome!</b>\n\nVideo khareedne ke liye neeche button par click karein:",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        pay_text = (
            f"💰 <b>Payment Details:</b>\n\n"
            f"• <b>Amount:</b> ₹{PRICE}\n"
            f"• <b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
            f"👉 Kisi bhi UPI app se payment karein aur <b>Screenshot</b> yahan bhej dein."
        )
        await query.edit_message_text(pay_text, parse_mode="HTML")

    # Admin Approve/Reject Logic
    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 <b>Payment Verified!</b>\n\nAapka video access link ye raha:\n{VIDEO_LINK}",
                parse_mode="HTML"
            )
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n✅ <b>STATUS: APPROVED</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            await query.edit_message_caption(caption=f"Error sending link: {e}")

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ <b>Payment Verification Failed!</b>\n\nAapka screenshot galat ya incomplete hai. Kripya sahi payment screenshot bhejein.",
                parse_mode="HTML"
            )
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n❌ <b>STATUS: REJECTED</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            await query.edit_message_caption(caption=f"Error: {e}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id

    # User ko notification
    await update.message.reply_text(
        "⏳ <b>Payment screenshot mil gaya!</b>\n\nAdmin ise verify kar rahe hain, kripya thoda wait karein...",
        parse_mode="HTML"
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
    first_name_clean = user.first_name.replace("<", "&lt;").replace(">", "&gt;") if user.first_name else "User"

    caption_text = (
        f"📩 <b>New Payment Screenshot!</b>\n\n"
        f"• <b>User:</b> {first_name_clean} ({username_str})\n"
        f"• <b>User ID:</b> <code>{user.id}</code>"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=caption_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
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
    
