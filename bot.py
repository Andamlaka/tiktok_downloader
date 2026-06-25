# bot.py — offers Audio or Video buttons

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from downloader import extract_audio, download_video

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Telegram won't let bots upload files bigger than 50 MB
MAX_SIZE = 50 * 1024 * 1024


# Step 1: user sends a link -> we show two buttons
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "tiktok.com" not in text:
        await update.message.reply_text("Send me a TikTok link and pick a format. 🙂")
        return

    # Remember this user's link so the button press knows what to download
    context.user_data["url"] = text

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio"),
        InlineKeyboardButton("🎬 Video (no watermark)", callback_data="video"),
    ]])
    await update.message.reply_text("What would you like?", reply_markup=buttons)


# Step 2: user taps a button -> we download and send
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # acknowledge the tap so the button stops "loading"

    choice = query.data
    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text("I lost the link — please send it again.")
        return

    await query.edit_message_text("⏳ Downloading...")

    try:
        if choice == "audio":
            path = extract_audio(url)
            with open(path, "rb") as f:
                await query.message.reply_audio(audio=f)
        else:
            path = download_video(url)
            if os.path.getsize(path) > MAX_SIZE:
                os.remove(path)
                await query.edit_message_text(
                    "❌ That video is over 50 MB — too big for Telegram bots. Try the audio instead."
                )
                return
            with open(path, "rb") as f:
                await query.message.reply_video(video=f)

        os.remove(path)
        await query.delete_message()

    except Exception as e:
        await query.edit_message_text(f"❌ Sorry, something went wrong:\n{e}")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("Bot is running... press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
