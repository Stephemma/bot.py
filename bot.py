from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from telegram.request import HTTPXRequest
import httpx

TOKEN = "8756387127:AAHPEDI_kWnnIJYYjutLPNnYopGHAqHb9aY"
ADMIN_ID = 6878072029
WALLET = "TEBZ3bqvDLZxk9udEQkqW9NF3ZhFAdz73b"
SUPPORT = "@Stephenemmanuel"
PROFIT_MARGIN = 0.10

ASKING_AMOUNT, ASKING_ACCOUNT_NUMBER, ASKING_ACCOUNT_NAME, ASKING_BANK_NAME = range(4)

async def get_live_rate():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=ngn",
                timeout=10
            )
            data = response.json()
            live_rate = data["tether"]["ngn"]
            return round(live_rate * (1 - PROFIT_MARGIN))
    except:
        return 1350

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to Esoft Crypto Exchange!*\n\n"
        "Esoft is a fast and reliable crypto to cash exchange service. "
        "We convert your USDT to Naira quickly and securely.\n\n"
        "📖 *How it works:*\n"
        "1. Check the current rate with /rate\n"
        "2. Use /sell to start a transaction\n"
        "3. Send your USDT to our wallet\n"
        "4. Provide your bank details\n"
        "5. Receive your Naira payment instantly!\n\n"
        "⚡ *Commands:*\n"
        "/rate — Check current exchange rate\n"
        "/sell — Sell your USDT for Naira\n"
        "/support — Get assistance",
        parse_mode="Markdown"
    )

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = await get_live_rate()
    await update.message.reply_text(
        f"📊 *Current Exchange Rate:*\n\n"
        f"1 USDT = ₦{rate:,}\n\n"
        f"Use /sell to start a transaction!",
        parse_mode="Markdown"
    )

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = await get_live_rate()
    await update.message.reply_text(
        f"💰 *Start a Transaction*\n\n"
        f"Current rate: 1 USDT = ₦{rate:,}\n\n"
        f"How much USDT do you want to sell?\n"
        f"Enter amount (e.g. 10):",
        parse_mode="Markdown"
    )
    return ASKING_AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
        rate = await get_live_rate()
        naira = amount * rate
        context.user_data["amount"] = amount
        context.user_data["naira"] = naira
        await update.message.reply_text(
            f"✅ *Transaction Summary:*\n\n"
            f"You sell: {amount} USDT\n"
            f"You receive: ₦{naira:,.0f}\n\n"
            f"📤 Send your USDT to this wallet:\n"
            f"`{WALLET}`\n\n"
            f"Please enter your *Account Number*:",
            parse_mode="Markdown"
        )
        return ASKING_ACCOUNT_NUMBER
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number!")
        return ASKING_AMOUNT

async def get_account_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["account_number"] = update.message.text
    await update.message.reply_text("Please enter your *Account Name*:", parse_mode="Markdown")
    return ASKING_ACCOUNT_NAME

async def get_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["account_name"] = update.message.text
    await update.message.reply_text("Please enter your *Bank Name*:", parse_mode="Markdown")
    return ASKING_BANK_NAME

async def get_bank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bank_name"] = update.message.text
    user = update.message.from_user
    amount = context.user_data["amount"]
    naira = context.user_data["naira"]
    account_number = context.user_data["account_number"]
    account_name = context.user_data["account_name"]
    bank_name = context.user_data["bank_name"]

    await update.message.reply_text(
        "⏳ *Transaction received!*\n\n"
        "Your transaction is being processed. "
        "You will be notified once payment is sent!",
        parse_mode="Markdown"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Payment", callback_data=f"confirm_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *New Sell Order!*\n\n"
             f"👤 From: {user.first_name} (@{user.username})\n"
             f"💰 Amount: {amount} USDT\n"
             f"💵 To Pay: ₦{naira:,.0f}\n\n"
             f"🏦 *Bank Details:*\n"
             f"Account Number: {account_number}\n"
             f"Account Name: {account_name}\n"
             f"Bank: {bank_name}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    action, user_id = data.split("_")
    user_id = int(user_id)

    if action == "confirm":
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ *Payment Confirmed!*\n\n"
                 "Your Naira payment has been sent to your account! "
                 "Thank you for using Esoft Crypto Exchange! 🎉",
            parse_mode="Markdown"
        )
        await query.edit_message_text("✅ Payment confirmed and customer notified!")
    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ *Transaction Failed!*\n\n"
                 "Unfortunately your transaction could not be processed. "
                 f"Please contact support: {SUPPORT}",
            parse_mode="Markdown"
        )
        await query.edit_message_text("❌ Transaction rejected and customer notified!")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💬 *Need Help?*\n\n"
        f"Contact our support directly:\n{SUPPORT}\n\n"
        f"We typically respond within minutes! 😊",
        parse_mode="Markdown"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Transaction cancelled!")
    return ConversationHandler.END

if __name__ == "__main__":
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = ApplicationBuilder().token(TOKEN).request(request).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("sell", sell)],
        states={
            ASKING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            ASKING_ACCOUNT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_account_number)],
            ASKING_ACCOUNT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_account_name)],
            ASKING_BANK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bank_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rate", rate))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Esoft Bot is running...")
    app.run_polling()
