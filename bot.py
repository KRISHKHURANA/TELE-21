from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
import requests

BOT_TOKEN = "8729755193:AAEmyoAEitdl1cVOZXEFYbS5-YUwJjAhcC0"
API_URL = "http://localhost:8000/print"

async def start(update, context):
    await update.message.reply_text("Send a photo and I will print it instantly! 🔥�")

async def handle_photo(update, context):
    # Get highest resolution photo
    file_id = update.message.photo[-1].file_id
    tg_file = await context.bot.get_file(file_id)

    # Download photo
    file_path = "temp.jpg"
    await tg_file.download_to_drive(file_path)

    # Send to FastAPI
    try:
        with open(file_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f})
        
        # Show success message
        await update.message.reply_text("Printing photo... 🖨️⚡")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling(drop_pending_updates=True)