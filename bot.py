import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image
from colorthief import ColorThief
import io

# Telegram Bot Token yahan dalein (BotFather se mila hua)
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check karein ki user ne photo bheji hai ya nahi
    photo = update.message.photo[-1] # Sabse high resolution image lein
    file = await context.bot.get_file(photo.file_id)
    
    # Image ko bytes mein download karein
    image_bytes = await file.download_as_bytearray()
    
    # Image open karein PIL ke zariye
    img = Image.open(io.BytesIO(image_bytes))
    
    # ColorThief se dominant color nikalein
    color_thief = ColorThief(io.BytesIO(image_bytes))
    dominant_color_rgb = color_thief.get_color(quality=1)
    dominant_hex = rgb_to_hex(dominant_color_rgb)
    
    # Palette se aur bhi colors nikalein (Header / Footer / Accents ke liye)
    palette_rgb = color_thief.get_palette(color_count=5)
    palette_hex = [rgb_to_hex(color) for color in palette_rgb]
    
    # ViMusic Style Theme Mapping
    background_color = dominant_hex # Darker dominant tone
    header_color = palette_hex[1] if len(palette_hex) > 1 else dominant_hex
    footer_color = palette_hex[2] if len(palette_hex) > 2 else dominant_hex
    accent_color = palette_hex[3] if len(palette_hex) > 3 else "#D0BCFF"

    # Response message format karein
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
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Jab bhi user image bhejega, yeh handler chalega
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("🤖 ViMusic Theme Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
