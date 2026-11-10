import os
import io
import threading
from flask import Flask
from telegram import InputFile, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

# 1. Flask server for Render port check
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "🤖 ViMusic Theme Bot with Canvas is running successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# 2. Telegram Bot Token
TOKEN = os.getenv("TOKEN")

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def create_canvas_image(color_mapping):
    """
    Extracted colors ka ek visual canvas (swatch strip) generate karta hai.
    """
    width = 800
    height = 250
    img = Image.new("RGB", (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    items = list(color_mapping.items())
    num_blocks = len(items)
    block_width = width // num_blocks
    
    for i, (label, hex_code) in enumerate(items):
        rgb = hex_to_rgb(hex_code)
        x0 = i * block_width
        x1 = (i + 1) * block_width if i < num_blocks - 1 else width
        y0 = 0
        y1 = height - 50 # Neeche text ke liye space chhodein
        
        # Color block draw karein
        draw.rectangle([x0, y0, x1, y1], fill=rgb)
        
        # Label aur Hex code likhein block ke neeche
        text_x = x0 + 15
        text_y = height - 40
        draw.text((text_x, text_y), f"{label}\n{hex_code}", fill=(255, 255, 255))
        
    bio = io.BytesIO()
    bio.name = 'palette_canvas.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    
    color_thief = ColorThief(io.BytesIO(image_bytes))
    dominant_color_rgb = color_thief.get_color(quality=1)
    dominant_hex = rgb_to_hex(dominant_color_rgb)
    
    palette_rgb = color_thief.get_palette(color_count=4)
    palette_hex = [rgb_to_hex(color) for color in palette_rgb]
    
    # ViMusic Style Theme Mapping Dictionary
    theme_colors = {
        "Background": dominant_hex,
        "Header": palette_hex[0] if len(palette_hex) > 0 else dominant_hex,
        "Footer": palette_hex[1] if len(palette_hex) > 1 else dominant_hex,
        "Accent": palette_hex[2] if len(palette_hex) > 2 else "#D0BCFF"
    }

    # Text message format
    response_text = (
        f"🎵 **ViMusic Dynamic Theme Extracted:**\n\n"
        f"🖼️ **Background:** `{theme_colors['Background']}`\n"
        f"📱 **Header:** `{theme_colors['Header']}`\n"
        f"📑 **Footer:** `{theme_colors['Footer']}`\n"
        f"✨ **Accent:** `{theme_colors['Accent']}`"
    )

    # Canvas Image generate karein
    canvas_bio = create_canvas_image(theme_colors)

    # Photo ke sath caption bhej dein
    await update.message.reply_photo(
        photo=InputFile(canvas_bio),
        caption=response_text,
        parse_mode="Markdown"
    )

def main():
    if not TOKEN:
        raise ValueError("No TOKEN found! Please set the TOKEN environment variable.")
        
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("🤖 ViMusic Theme Bot with Canvas is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
