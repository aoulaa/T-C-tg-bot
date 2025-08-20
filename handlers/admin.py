import logging
import csv
import io
from aiogram import Router, Bot, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from db.database import set_voice_only_mode, get_voice_only_mode, get_all_user_acceptances, get_all_group_settings
from config import BOT_OWNER_ID

router = Router()


async def is_admin(message: Message, bot: Bot) -> bool:
    """Checks if the message author is an admin or creator of the chat."""
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}


@router.message(Command("voiceonly_on"))
async def voice_only_on(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.reply("Only admins can use this command.")

    chat_id = message.chat.id
    chat_title = message.chat.title
    chat_mode = "on"

    await set_voice_only_mode(chat_id, chat_title, chat_mode)
    await message.reply("Voice-only mode has been enabled. I will now delete all non-voice messages.")
    logging.info(f"Voice-only mode enabled for chat {chat_id} by user {message.from_user.id}")


@router.message(Command("voiceonly_off"))
async def voice_only_off(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.reply("Only admins can use this command.")

    chat_id = message.chat.id
    chat_title = message.chat.title
    chat_mode = "off"
    await set_voice_only_mode(chat_id, chat_title, chat_mode)
    await message.reply("Voice-only mode has been disabled. All message types are now allowed.")
    logging.info(f"Voice-only mode disabled for chat {chat_id} by user {message.from_user.id}")


# --- Owner-only commands ---

@router.message(Command("export_users"))
async def export_users(message: Message):
    """Owner-only: Exports the user acceptance list as a CSV file."""
    if message.from_user.id != int(BOT_OWNER_ID):
        return await message.reply("Only the bot owner can use this command.")
    if message.chat.type != 'private':
        return await message.reply("This command must be used in a private chat.")

    users = await get_all_user_acceptances()

    await message.reply("Exporting user data...")

    if not users:
        return await message.reply("No users have accepted the T&C yet.")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['user_id', 'username', 't_and_c_version', 'timestamp', 'chat_id', 't_and_c_content'])
    for user in users:
        writer.writerow([user['user_id'], user['username'], user['t_and_c_version'], user['timestamp'], user['chat_id'], user['t_and_c_content']])

    output.seek(0)
    csv_file = BufferedInputFile(output.getvalue().encode('utf-8'), filename="user_acceptances.csv")

    await message.reply_document(csv_file, caption="Here is the list of users who have accepted the T&C.")
    logging.info(f"Bot owner {message.from_user.id} exported user data.")


@router.message(Command("show_groups"))
async def show_groups(message: Message):
    """Owner-only: Shows the settings for all groups."""
    if message.from_user.id != int(BOT_OWNER_ID):
        return await message.reply("Only the bot owner can use this command.")
    if message.chat.type != 'private':
        return await message.reply("This command must be used in a private chat.")

    groups = await get_all_group_settings()
    if not groups:
        return await message.reply("The bot has not been configured in any groups yet.")

    response_text = "**Group Settings:**\n\n"
    for group in groups:
        response_text += f"Chat Name: `{group['chat_title']}`\nVoice Only Mode: **{group['voice_only_mode'].upper()}**\n\n"

    await message.reply(response_text, parse_mode="MarkdownV2")
    logging.info(f"Bot owner {message.from_user.id} requested group settings.")


# This handler must be last to not override commands
@router.message(F.chat.type.in_(["group", "supergroup"]))
async def delete_non_voice_messages(message: Message, bot: Bot):
    """Deletes any message that is not a voice message in voice-only chats."""
    chat_id = message.chat.id
    mode = await get_voice_only_mode(chat_id)

    if mode == 'on':
        if await is_admin(message, bot):
            return

        if message.voice:
            return

        try:
            await message.delete()
            logging.info(f"Deleted non-voice message from {message.from_user.id} in chat {chat_id}")
        except Exception as e:
            logging.error(f"Failed to delete message in chat {chat_id}: {e}")
