import os 
import logging 
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.ext import CallbackQueryHandler

from groq import Groq

logging.basicConfig( 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO 
) 
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logger.info(f"Loaded TELEGRAM_TOKEN: {bool(TELEGRAM_TOKEN)}") 
logger.info(f"Loaded GROQ_API_KEY: {bool(GROQ_API_KEY)}")

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
"Welcome to the Official bot of ahrWWR™ "
        "Please select your language 👉:"
    )

    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
            InlineKeyboardButton("Nederlands", callback_data="lang_nl"),
            InlineKeyboardButton("Persian", callback_data="lang_fa")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lang_en":
        await query.edit_message_text("Language set to English")
    elif query.data == "lang_nl":
        await query.edit_message_text("Taal ingesteld op Nederlands")
    elif query.data == "lang_fa":
        await query.edit_message_text("زبان به فارسی تغییر یافت")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_text = update.message.text

    if len(user_text) > 8000:
        user_text = user_text[:8000]
    logger.info(f"User said: {user_text}")
    if not user_text.strip():
        await update.message.reply_text("Please Send Me a Message So I Can Reply 🔥")
        return

    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=8192,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ]
        )
        answer = response.choices[0].message.content

        def split_message(text, limit=4000):
            return [text[i:i+limit] for i in range(0, len(text), limit)]

        for part in split_message(answer):
            await update.message.reply_text(part)
        
        logger.info("Reply sent successfully.")
    except Exception as e:
        await update.message.reply_text(f"Error details: {e}")
    
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

app.run_polling()
