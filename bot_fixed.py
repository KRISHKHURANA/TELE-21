from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import asyncio

BOT_TOKEN = "8729755193:AAEmyoAEitdl1cVOZXEFYbS5-YUwJjAhcC0"
API_URL = "http://localhost:8000/print"

async def start(update, context):
    await update.message.reply_text("Send a photo and I will print it instantly! 🖨️")

async def handle_photo(update, context):
    try:
        # Get highest resolution photo
        file_id = update.message.photo[-1].file_id
        tg_file = await context.bot.get_file(file_id)

        # Download photo
        file_path = "temp.jpg"
        await tg_file.download_to_drive(file_path)

        # Send to FastAPI
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            await update.message.reply_text("✅ Printing photo... 🖨️")
        else:
            await update.message.reply_text("❌ Print failed. Please try again.")
            
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def main():
    # Create application with longer timeout
    app = (Application.builder()
           .token(BOT_TOKEN)
           .connect_timeout(30)
           .read_timeout(30)
           .write_timeout(30)
           .build())
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Initialize and start
    print("Initializing bot...")
    await app.initialize()
    print("Starting bot...")
    await app.start()
    print("Bot started successfully!")
    
    # Run polling
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Stopping bot...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())