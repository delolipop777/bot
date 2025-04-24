import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)
from fastapi import FastAPI, Request
from telegram import Bot
from telegram.ext import Dispatcher

# Registration steps
NAME, PHONE, VISIT_TIME, GUEST_COUNT = range(4)

# Admin ID
ADMIN_ID = 386753959

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# Telegram bot webhook endpoint
@app.post("/webhook")
async def handle_webhook(request: Request):
    update = Update.de_json(await request.json(), bot)
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.process_update(update)
    return {"status": "ok"}

# Bot logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Assalomu alaykum! 👋\n"
        "Sizni tashrif vaqti va ma'lumotlaringizni qayd etish uchun botimizga xush kelibsiz. 😊\n\n"
        "Iltimos, quyidagi ma'lumotlarni kiriting:\n"
        "1️⃣ Ism-familiya\n"
        "2️⃣ Telefon raqamingiz\n"
        "3️⃣ Tashrif vaqti (tanlash uchun tugmani bosing)\n"
        "4️⃣ Tashrif buyuruvchilar soni\n\n"
        "Keling, boshqacha boshlaymiz! 😃"
    )
    await update.message.reply_text(welcome_message)
    await update.message.reply_text("Ism-familiyangizni kiriting:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting (masalan, +998XXXXXXXXX):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("14:00", callback_data="14:00")],
        [InlineKeyboardButton("15:00", callback_data="15:00")],
        [InlineKeyboardButton("16:00", callback_data="16:00")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Tashrif vaqti tanlang:", reply_markup=reply_markup)
    return VISIT_TIME

async def visit_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    visit_time = query.data
    context.user_data["visit_time"] = visit_time

    await query.answer()
    await query.edit_message_text(f"Tashrif vaqti: {visit_time}.\nEndi, tashrif buyuruvchilar sonini kiriting:")
    return GUEST_COUNT

async def get_guest_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guest_count = update.message.text
    if not guest_count.isdigit() or int(guest_count) <= 0:
        await update.message.reply_text("Iltimos, to'g'ri raqam kiriting (1 va undan katta son).")
        return GUEST_COUNT

    context.user_data["guest_count"] = guest_count
    name = context.user_data["name"]
    phone = context.user_data["phone"]
    visit_time = context.user_data["visit_time"]

    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or "N/A"
    username = update.message.from_user.username or "N/A"

    message = (
        f"📥 Yangi tashrif buyuruvchidan ma'lumot:\n"
        f"👤 Ism-familiya: {name}\n"
        f"📞 Telefon raqami: {phone}\n"
        f"🕓 Tashrif vaqti: {visit_time}\n"
        f"👥 Tashrif buyuruvchilar soni: {guest_count}\n\n"
        f"🔑 Foydalanuvchi haqida qo'shimcha ma'lumot:\n"
        f"First Name: {first_name}\n"
        f"Last Name: {last_name}\n"
        f"Username: @{username}\n"
        f"User ID: {update.message.from_user.id}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Tashrif ma'lumotlaringiz muvaffaqiyatli yuborildi! 👌")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tashrif ro'yxatdan o'tkazish bekor qilindi.")
    return ConversationHandler.END

if __name__ == "__main__":
    # Set webhook URL
    webhook_url = "https://bot.railway.app/webhook"
    bot.set_webhook(url=webhook_url)

    # Run FastAPI with Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
