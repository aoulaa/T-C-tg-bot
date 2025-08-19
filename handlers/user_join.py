import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ChatPermissions

from config import TERMS_AND_CONDITIONS, T_AND_C_VERSION
from db.database import add_user_acceptance
from keyboards.inline import get_tc_keyboard

router = Router()

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

        # Ignore bots
        if user.is_bot:
            continue

        logging.info(f"New user {user.id} ({user.full_name}) joined chat {chat_id}. Restricting permissions.")

        # Restrict the user immediately
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=RESTRICTED_PERMISSIONS
        )

        text = (
            f"Welcome, {user.full_name}!"
            f"{TERMS_AND_CONDITIONS.format(version=T_AND_C_VERSION)}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=get_tc_keyboard(user.id)
        )


@router.callback_query(F.data.startswith("user_accept:"))
async def process_tc_accept(callback_query: CallbackQuery, bot: Bot):
    """This handler triggers when a user clicks the 'Accept' button."""
    target_user_id = int(callback_query.data.split(":")[1])
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

    await add_user_acceptance(user_who_clicked.id, user_who_clicked.username, T_AND_C_VERSION)

    await callback_query.message.delete()

    await bot.send_message(chat_id, f"{user_who_clicked.mention_html()} has accepted the T&C and can now participate.")