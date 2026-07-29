import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- AAPKI DETAILS ---
BOT_TOKEN = "8540523678:AAEHMG-UnKmb8oUB5pWOIJeo0oVYwNII3UE"  # Aapka Bot Token
VIDEO_LINK = "https://t.me/+L9-IXAW3cixHMmM1"                 # Aapka Channel/Video Link
UPI_ID = "9337091479@fam"                                      # Aapki UPI ID
PRICE = "149"                                                  # Price ₹149

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"💳 Buy Video (₹{PRICE})", callback_data='buy')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 **Welcome!**\n\nVideo khareedne ke liye neeche button par click karein:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'buy':
        pay_text = (
            f"💰 **Payment Details:**\n\n"
            f"🔹 **Amount:** ₹{PRICE}\n"
            f"🔹 **UPI ID:** `{UPI_ID}`\n\n"
            f"👉 Kisi bhi UPI app (PhonePe/Paytm/GooglePay) se payment karein.\n"
            f"Payment hone ke baad, **Screenshot** yahan chat me bhej dein."
        )
        await query.edit_message_text(pay_text, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Payment screenshot mil gaya! Verifying...")
    await update.message.reply_text(
        f"🎉 **Payment Successful!**\n\nAapka video access link ye raha 👇\n{VIDEO_LINK}"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

