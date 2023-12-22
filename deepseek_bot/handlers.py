import asyncio
import typing as ty
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
)
from telegram.error import NetworkError, BadRequest
from telegram.constants import ChatAction, ParseMode
from deepseek_bot.deepseek import deepseek, generate_response
from deepseek_bot.html_format import format_message

chats: dict[str, ty.Any] = {}

async def new_chat(chat_id: int, model: str) -> None:
    if chat_id in chats:
        chats[chat_id]["chat"].close()
    ds = await deepseek(model)
    chats[chat_id] = {
        "chat": ds,
    }


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\nStart sending messages with me to generate a response.\n\nSend /new to start a new chat session.",
        # reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
Basic commands:
/start - Start the bot
/help - Get help. Shows this message

Chat commands:
/new - Start a new chat session (model will forget previously generated messages)

Send a message to the bot to generate a response.
"""
    await update.message.reply_text(help_text)
    
    
async def handle_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    init_msg = await update.message.reply_text(
        text="Generating response...",
        reply_to_message_id=update.message.message_id,
    )
    if update.message.chat.id not in chats:
        await init_msg.edit_text(
            "Choose a model to start a new chat session:",
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Deepseek Chat 67B", callback_data="new_chat_deepseek_chat")],
                [InlineKeyboardButton("Deepseek Code 33B", callback_data="new_chat_deepseek_code")],
            ]),
        )
        return
    deepseek = chats[update.message.chat_id]["chat"]
    prompt = update.message.text
    full_response = ""
    async for message in generate_response(deepseek,prompt):
        try:
            if message:
                full_response += message
                formatted_message = format_message(full_response)
                
                # Telegram message length limit is 4096 characters
                if len(formatted_message) > 4096:
                    formatted_message = formatted_message[4096:]
                    init_msg = await init_msg.reply_text(
                        text=formatted_message,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=init_msg.message_id,
                        disable_web_page_preview=True,
                    )
                else:
                    if init_msg.text != "Generating response...":
                        init_msg = await init_msg.edit_text(
                            text=formatted_message,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )
                    else:
                        init_msg = await init_msg.edit_text(
                            text=formatted_message,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )
        except Exception as e:
            print(e)
            await init_msg.edit_text(
                text="Error generating response.",
            )
            break
        await asyncio.sleep(0.1)
            


async def newchat_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session."""
    init_msg = await update.message.reply_text(
        text="Starting new chat session...",
        reply_to_message_id=update.message.message_id,
    )
    
    await init_msg.edit_text(
        "Choose a model to start a new chat session:",
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Deepseek Chat 67B", callback_data="new_chat_deepseek_chat")],
            [InlineKeyboardButton("Deepseek Code 33B", callback_data="new_chat_deepseek_code")],
        ]),
    )
    
    
async def new_chat_callback_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session."""
    init_msg = await update.callback_query.message.edit_text(
        text="Starting new chat session...",
        reply_markup=None,
    )
    model = update.callback_query.data.replace("new_chat_", "")
    await new_chat(update.callback_query.message.chat.id, model)
    await init_msg.edit_text(
        text="Started new `" + model + "` chat session\.",
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await update.callback_query.answer()
