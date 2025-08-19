import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv

from db.database import init_db
from handlers import user_join

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(user_join.router)


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` command"""
    await message.reply("Hello! I am the community bot, ready to manage join requests.")


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
