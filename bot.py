import os 
import logging 
from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters 
from openai import OpenAI

logging.basicConfig( 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO 
) 
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger.info(f"Loaded TELEGRAM_TOKEN: {bool(TELEGRAM_TOKEN)}") 
logger.info(f"Loaded OPENAI_API_KEY: {bool(OPENAI_API_KEY)}")

client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("AI bot is online and ready.")
    
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_text = update.message.text 
    logger.info(f"User said: {user_text}")
    
    try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_text}]
    )
    answer = response.choices[0].message.content
    await update.message.reply_text(answer)
    logger.info("Reply sent successfully.")
except Exception as e:
    logger.error(f"OpenAI error: {e}")
    await update.message.reply_text("An internal error occurred, but the bot is still running.")
    
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() 
app.add_handler(CommandHandler("start", start)) 
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

logger.info("AI Bot is running...") 
app.run_polling()
