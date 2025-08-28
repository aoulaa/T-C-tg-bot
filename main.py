import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBHOOK_PORT, BOT_OWNER_ID
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
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info("Webhook set successfully")
    except Exception as e:
        # Do not crash the app if Telegram can't set the webhook (e.g., DNS/cert issues)
        logging.exception(f"Failed to set webhook to {WEBHOOK_URL}: {e}")

    # Register bot commands so they appear on '/'
    try:
        # Default (applies everywhere unless a more specific scope overrides)
        await bot.set_my_commands([
            types.BotCommand(command="start", description="Start the bot"),
        ], scope=types.BotCommandScopeDefault())

        # All group chats (admins can see/use voice-only toggles)
        await bot.set_my_commands([
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="voiceonly_on", description="Enable voice-only mode (admin)"),
            types.BotCommand(command="voiceonly_off", description="Disable voice-only mode (admin)"),
        ], scope=types.BotCommandScopeAllGroupChats())

        # Bot owner's private chat: include owner-only commands
        owner_chat_id = int(BOT_OWNER_ID)
        await bot.set_my_commands([
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="export_users", description="Owner: export users CSV"),
            types.BotCommand(command="show_groups", description="Owner: list group settings"),
        ], scope=types.BotCommandScopeChat(chat_id=owner_chat_id))

        logging.info("Bot commands registered (scoped)")
    except Exception as e:
        logging.exception(f"Failed to set bot commands: {e}")


async def on_shutdown(bot: Bot):
    logging.info("Deleting webhook...")
    try:
        await bot.delete_webhook()
    except Exception as e:
        logging.exception(f"Failed to delete webhook: {e}")


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

    # Health endpoint for quick checks
    async def healthz(_request: web.Request) -> web.Response:
        return web.Response(text="ok")
    app.router.add_get("/healthz", healthz)

    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT)


if __name__ == "__main__":
    main()
