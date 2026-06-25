# bot.py — offers Audio or Video buttons, with a welcome message

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from downloader import extract_audio, download_video

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MAX_SIZE = 50 * 1024 * 1024  # Telegram's 50 MB upload limit for bots

WELCOME = (
    "👋 *Welcome to the TikTok Downloader!*\n\n"
    "📌 *How to use me:*\n"
    "1️⃣ Copy a TikTok link (in TikTok: Share → Copy Link)\n"
    "2️⃣ Paste it here in the chat\n"
    "3️⃣ Choose 🎵 *Audio* or 🎬 *Video (no watermark)*\n\n"
    "Go ahead — send me a TikTok link! 🎬"
)


# Runs on /start and /help
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode="Markdown")


# User sends a link -> show two buttons
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "tiktok.com" not in text:
        await update.message.reply_text(
            "❗ That doesn't look like a TikTok link.\n\n"
            "Please paste a TikTok video link (Share → Copy Link)."
        )
        return

    context.user_data["url"] = text

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio"),
        InlineKeyboardButton("🎬 Video (no watermark)", callback_data="video"),
    ]])
    await update.message.reply_text("✅ Got your link! What would you like?", reply_markup=buttons)


# User taps a button -> download and send
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text("I lost the link — please send it again.")
        return

    await query.edit_message_text("⏳ Downloading, please wait...")

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
    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("Bot is running... press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
