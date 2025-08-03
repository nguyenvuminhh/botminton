from commands.start import start
from config import BOT_TOKEN
from constants import Commands
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler(Commands.START, start))

    app.start_polling()

if __name__ == "__main__":
    run()