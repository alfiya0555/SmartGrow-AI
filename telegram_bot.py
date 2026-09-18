import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_FILE = "chat_id.txt"  # File to store the user's chat ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command: Register chat ID and greet."""
    chat_id = update.effective_chat.id
    # Save chat ID to file (for alerts from Flask)
    try:
        with open(CHAT_ID_FILE, "w") as f:
            f.write(str(chat_id))
        await update.message.reply_text(
            "Hello! I'm your SmartGrow bot. Send me a message, and I'll echo it back. "
            "Alerts will be sent here automatically."
        )
    except Exception as e:
        await update.message.reply_text("Hello! Couldn't save chat ID, but I can still reply.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages: Echo them back (customize as needed)."""
    text = update.message.text
    chat_id = update.effective_chat.id
    
    # Example: Echo the message back
    reply = f"{text}"
    
    # Customize here: e.g., check for keywords like "status" to fetch sensor data
    if text.lower() == "status":
        # Fetch latest data from Flask (similar to your original bot)
        reply = "Fetching status... (integrate with Flask here)"
        # Add code to call Flask /get_latest and format response
    
    # Send reply
    await update.message.reply_text(reply)

def main():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN not set in .env")
        return
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running... Send /start in Telegram to begin.")
    application.run_polling()

if __name__ == "__main__":
    main()
