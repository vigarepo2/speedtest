#!/usr/bin/env python3
import logging
import math
from speedtest import Speedtest, ConfigRetrievalError
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging to show live logs in the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Function to convert file size to a readable format
def get_readable_file_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_in_bytes, 1024)))
    p = math.pow(1024, i)
    readable_size = round(size_in_bytes / p, 2)
    return f"{readable_size} {size_name[i]}"

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    message = "Hello! I am your bot. Use /speedtest to check internet speed or /help to see all commands."
    await update.message.reply_text(message)
    logging.info(f"User {update.effective_user.id} used /start command.")

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler."""
    message = (
        "Available Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/speedtest - Check internet speed"
    )
    await update.message.reply_text(message)
    logging.info(f"User {update.effective_user.id} used /help command.")

# Command: /speedtest
async def speedtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run speed test and send results."""
    message = await update.message.reply_text("<i>Initiating Speedtest...</i>", parse_mode="HTML")
    try:
        # Perform speed test
        test = Speedtest()
        test.get_best_server()
        test.download()
        test.upload()
        test.results.share()
        result = test.results.dict()
        path = result['share']

        # Format results
        speed_info = f"""
➲ <b><i>SPEEDTEST INFO</i></b>
┠ <b>Upload:</b> <code>{get_readable_file_size(result['upload'] / 8)}/s</code>
┠ <b>Download:</b> <code>{get_readable_file_size(result['download'] / 8)}/s</code>
┠ <b>Ping:</b> <code>{result['ping']} ms</code>
┠ <b>Time:</b> <code>{result['timestamp']}</code>
┠ <b>Data Sent:</b> <code>{get_readable_file_size(int(result['bytes_sent']))}</code>
┖ <b>Data Received:</b> <code>{get_readable_file_size(int(result['bytes_received']))}</code>

➲ <b><i>SPEEDTEST SERVER</i></b>
┠ <b>Name:</b> <code>{result['server']['name']}</code>
┠ <b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
┠ <b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
┠ <b>Latency:</b> <code>{result['server']['latency']}</code>
┠ <b>Latitude:</b> <code>{result['server']['lat']}</code>
┖ <b>Longitude:</b> <code>{result['server']['lon']}</code>

➲ <b><i>CLIENT DETAILS</i></b>
┠ <b>IP Address:</b> <code>{result['client']['ip']}</code>
┠ <b>Latitude:</b> <code>{result['client']['lat']}</code>
┠ <b>Longitude:</b> <code>{result['client']['lon']}</code>
┠ <b>Country:</b> <code>{result['client']['country']}</code>
┠ <b>ISP:</b> <code>{result['client']['isp']}</code>
┖ <b>ISP Rating:</b> <code>{result['client']['isprating']}</code>
"""
        await update.message.reply_photo(photo=path, caption=speed_info, parse_mode="HTML")
        await message.delete()
    except ConfigRetrievalError:
        await message.edit_text("<b>ERROR:</b> <i>Can't connect to the server at the moment. Try again later!</i>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"Speedtest error: {e}")
        await message.edit_text(f"<b>ERROR:</b> {str(e)}", parse_mode="HTML")

# Echo all other messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo all user messages."""
    user_message = update.message.text
    await update.message.reply_text(user_message)
    logging.info(f"User {update.effective_user.id} sent a message: {user_message}")

# Main function
if __name__ == '__main__':
    TOKEN = "7958850882:AAFb5Es85rQBURYdSIr5w4q9SRTSO6XmB3Y"  # Replace with your bot token
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("speedtest", speedtest_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot
    logging.info("Bot is starting...")
    app.run_polling()
