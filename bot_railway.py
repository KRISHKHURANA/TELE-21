import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! Send me a photo and I will process it for you! 📸\n'
        'Note: This is a cloud version - printing functionality is not available.'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages."""
    try:
        # Get the photo file
        photo_file = await update.message.photo[-1].get_file()
        
        # Download photo to memory (Railway has ephemeral storage)
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Process the photo (placeholder for your logic)
        file_size = len(photo_bytes)
        
        await update.message.reply_text(
            f'✅ Photo received successfully!\n'
            f'📏 Size: {file_size} bytes\n'
            f'🔧 Processing completed!\n\n'
            f'Note: This is the cloud version. For printing, use the local version.'
        )
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            '❌ Sorry, there was an error processing your photo. Please try again.'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 *Bot Commands:*
/start - Start the bot
/help - Show this help message

📸 *How to use:*
Just send me any photo and I'll process it for you!

ℹ️ *Note:* This is the cloud version running on Railway. 
For local printing functionality, use the desktop version.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Get port from environment variable (Railway provides this)
    port = int(os.getenv('PORT', 8000))
    
    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()