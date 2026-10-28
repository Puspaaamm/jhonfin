import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Token aur App URL configure karein
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 5000))
RENDER_URL = os.getenv("RENDER_URL", "YOUR_RENDER_APP_URL")

app = Flask(__name__)

# Specific WikiProjects aur Requested Articles ki List
TODO_MESSAGE = (
    "👋 **Hello! Yeh lijiye Wikipedia ke चुनिंदा WikiProjects aur Requested Articles ke links:**\n\n"
    "🔬 **1. विज्ञान, प्रौद्योगिकी और तकनीक (Science & Technology)**\n"
    "• [WikiProject Science](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Science)\n"
    "• [WikiProject Computer Science](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Computer_science)\n"
    "• [WikiProject Physics](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Physics)\n"
    "• [WikiProject Chemistry](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Chemistry)\n"
    "• [WikiProject Mathematics](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Mathematics)\n"
    "• [WikiProject Electronics](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Electronics)\n"
    "• [WikiProject Medicine](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Medicine)\n\n"

    "🌍 **2. इतिहास, भूगोल और समाज (History, Geography & Society)**\n"
    "• [WikiProject History](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_History)\n"
    "• [WikiProject Biography](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Biography)\n"
    "• [WikiProject Geography](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Geography)\n"
    "• [WikiProject Countries](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Countries)\n"
    "• [WikiProject India](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_India)\n"
    "• [WikiProject Military History](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Military_history)\n\n"

    "🎬 **3. कला, संस्कृति और मनोरंजन (Arts & Entertainment)**\n"
    "• [WikiProject Film](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Film)\n"
    "• [WikiProject Music](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Music)\n"
    "• [WikiProject Television](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Television)\n"
    "• [WikiProject Video Games](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Video_games)\n"
    "• [WikiProject Architecture](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Architecture)\n\n"

    "📌 **4. Wikipedia Requested Articles**\n"
    "• [Main Requested Articles](https://en.wikipedia.org/wiki/Wikipedia:Requested_articles)\n"
    "• [Requested Articles by Subject](https://en.wikipedia.org/wiki/Wikipedia:Requested_articles/ByCategory)\n\n"
    "Aap in links par click karke direct pages par ja sakte hain!"
)

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
    app.run(host="0.0.0.0", port=PORT)
