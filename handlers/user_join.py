import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ChatPermissions, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import T_AND_C_VERSION, T_AND_C_CONTENT
from db.database import add_user_acceptance

router = Router()

def escape_markdown_v2(text: str) -> str:
    """Manually escape characters for Telegram's MarkdownV2 parser."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join([f'\\{char}' if char in escape_chars else char for char in text])


RESTRICTED_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

UNRESTRICTED_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True
)


@router.message(F.new_chat_members)
async def on_user_join(message: Message, bot: Bot):
    """This handler triggers when a new user joins the chat."""
    for user in message.new_chat_members:
        chat_id = message.chat.id

        if user.is_bot:
            continue

        logging.info(f"New user {user.id} ({user.full_name}) joined chat {chat_id}. Restricting permissions.")

        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=RESTRICTED_PERMISSIONS
        )

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="✅ Accept", callback_data=f"accept_t&c_{user.id}"))

        if T_AND_C_CONTENT.startswith('http'):
            # Escape the version string for MarkdownV2, but not the URL itself.
            version_safe = escape_markdown_v2(T_AND_C_VERSION)
            message_text = f"To join this group, please review and accept our [Terms & Conditions]({T_AND_C_CONTENT}) \\(version {version_safe}\\)\\."
            parse_mode = "MarkdownV2"
        else:
            message_text = f"**Terms & Conditions**\n\n{T_AND_C_CONTENT}\n\nBy clicking 'Accept', you agree to our T&C version {T_AND_C_VERSION}."
            parse_mode = "Markdown"

        await bot.send_message(
            chat_id=chat_id,
            text=message_text,
            reply_markup=keyboard.as_markup(),
            parse_mode=parse_mode
        )


@router.callback_query(F.data.startswith("accept_t&c_"))
async def process_tc_accept(callback_query: CallbackQuery, bot: Bot):
    """This handler triggers when a user clicks the 'Accept' button."""
    target_user_id = int(callback_query.data.split("_")[2])
    user_who_clicked = callback_query.from_user

    if user_who_clicked.id != target_user_id:
        await callback_query.answer("This button is not for you.", show_alert=True)
        return

    chat_id = callback_query.message.chat.id
    logging.info(f"User {user_who_clicked.id} accepted T&C in chat {chat_id}. Lifting restrictions.")

    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_who_clicked.id,
        permissions=UNRESTRICTED_PERMISSIONS
    )

    await add_user_acceptance(user_who_clicked.id, chat_id, user_who_clicked.username, T_AND_C_VERSION, T_AND_C_CONTENT)

    await callback_query.message.delete()

    await bot.send_message(chat_id, f"{user_who_clicked.full_name} has accepted the T&C and can now participate.")