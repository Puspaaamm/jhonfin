import os
import io
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image
from colorthief import ColorThief

# 1. Chhota sa Flask app banayein taaki Render ka port requirement poora ho jaye
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "🤖 ViMusic Theme Bot is running successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# 2. Telegram Bot Logic
TOKEN = os.getenv("TOKEN")

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    
    color_thief = ColorThief(io.BytesIO(image_bytes))
    dominant_color_rgb = color_thief.get_color(quality=1)
    dominant_hex = rgb_to_hex(dominant_color_rgb)
    
    palette_rgb = color_thief.get_palette(color_count=5)
    palette_hex = [rgb_to_hex(color) for color in palette_rgb]
    
    background_color = dominant_hex
    header_color = palette_hex[1] if len(palette_hex) > 1 else dominant_hex
    footer_color = palette_hex[2] if len(palette_hex) > 2 else dominant_hex
    accent_color = palette_hex[3] if len(palette_hex) > 3 else "#D0BCFF"

    response_text = (
        f"🎵 **ViMusic Dynamic Theme Palette Extracted:**\n\n"
        f"🖼️ **Background Color:** `{background_color}`\n"
        f"📱 **Header Color:** `{header_color}`\n"
        f"📑 **Footer Color:** `{footer_color}`\n"
        f"✨ **Accent / Highlight:** `{accent_color}`\n\n"
        f"🎨 **Full Palette HEX Codes:**\n"
        f"• " + "\n• ".join([f"`{code}`" for code in palette_hex])
    )

    await update.message.reply_text(response_text, parse_mode="Markdown")

def main():
    if not TOKEN:
        raise ValueError("No TOKEN found! Please set the TOKEN environment variable.")
        
    # Flask server ko alag thread mein start karein
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Telegram bot app start karein
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("🤖 ViMusic Theme Bot is running with Flask web server...")
    app.run_polling()

if __name__ == "__main__":
    main()
