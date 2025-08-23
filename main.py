import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBHOOK_PORT
from db.database import init_db
from handlers import user_join, admin

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` command"""
    await message.reply("Hello! I am the community bot, ready to manage join requests.")


async def on_startup(bot: Bot):
    logging.info("Initializing database...")
    await init_db()
    logging.info(f"Setting webhook to {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(bot: Bot):
    logging.info("Deleting webhook...")
    await bot.delete_webhook()


def main():
    logging.info("Starting bot...")
    # Register handlers
    dp.include_router(user_join.router)
    dp.include_router(admin.router)

    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Create aiohttp application
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT)


if __name__ == "__main__":
    main()
