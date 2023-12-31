import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from deepseek_bot.handlers import (
    start,
    help_command,
    handle_message,
    newchat_command,
    new_chat_callback_handler,
)
from deepseek_bot.filters import AuthFilter, MessageFilter
from dotenv import load_dotenv

load_dotenv()


def start_bot():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start, filters=AuthFilter))
    app.add_handler(CommandHandler("help", help_command, filters=AuthFilter))
    app.add_handler(CommandHandler("new", newchat_command, filters=AuthFilter))
    app.add_handler(MessageHandler(MessageFilter, handle_message))
    app.add_handler(
        CallbackQueryHandler(new_chat_callback_handler, pattern="^new_chat_")
    )

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)
