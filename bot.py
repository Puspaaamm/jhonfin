import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Token aur App URL configure karein
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 5000))
# Render ka URL yahan dalein (jaise https://my-telegram-bot.onrender.com)
RENDER_URL = os.environ.get("RENDER_URL", "YOUR_RENDER_APP_URL")

app = Flask(__name__)

TODO_MESSAGE = (
    "👋 **Hello! Yeh lijiye Wikipedia ke requested articles aur to-do lists ke links:**\n\n"
    "📋 **1. English Wikipedia To-Do Lists (All Projects):**\n"
    "• [Wikipedia:Community portal/ToDo](https://en.wikipedia.org/wiki/Wikipedia:Community_portal/ToDo)\n"
    "• [Wikipedia:Task Directory](https://en.wikipedia.org/wiki/Wikipedia:Task_Directory)\n\n"
    "📌 **2. Wikipedia:Requested Articles Lists:**\n"
    "• [Main Requested Articles Page](https://en.wikipedia.org/wiki/Wikipedia:Requested_articles)\n"
    "• [Requested Articles by Subject](https://en.wikipedia.org/wiki/Wikipedia:Requested_articles/ByCategory)\n\n"
    "Aap in links par click karke direct pages par ja sakte hain!"
)

# Telegram Application ko globally initialize karein
telegram_app = None

async def setup_bot():
    global telegram_app
    if telegram_app is None:
        telegram_app = ApplicationBuilder().token(TOKEN).build()
        
        async def start_and_hi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_text = update.message.text.lower()
            if 'hi' in user_text or 'hello' in user_text or '/start' in user_text:
                await update.message.reply_text(
                    TODO_MESSAGE, 
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )

        telegram_app.add_handler(CommandHandler("start", start_and_hi_handler))
        telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start_and_hi_handler))
        
        await telegram_app.initialize()
    return telegram_app

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Telegram se aane wale updates ko handle karne ke liye endpoint"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process():
        application = await setup_bot()
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        
    loop.run_until_complete(process())
    return "OK", 200

@app.route("/")
def home():
    return "Bot is running on Render!"

if __name__ == "__main__":
    # Local testing ke liye ya Gunicorn ke through run hoga
    app.run(host="0.0.0.0", port=PORT)
