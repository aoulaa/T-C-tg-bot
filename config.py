# config.py
import os

from dotenv import load_dotenv

load_dotenv()


# Version of the Terms and Conditions
T_AND_C_VERSION = os.getenv("T_AND_C_VERSION")
if not T_AND_C_VERSION:
    raise ValueError("No T_AND_C_VERSION found in environment variables")

# The content of the Terms and Conditions (can be a string or a URL)
T_AND_C_CONTENT = os.getenv("T_AND_C_CONTENT")
if not T_AND_C_CONTENT:
    raise ValueError("No T_AND_C_CONTENT found in environment variables")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME")

BOT_OWNER_ID = os.getenv("BOT_OWNER_ID")
if not BOT_OWNER_ID:
    raise ValueError("No BOT_OWNER_ID found in environment variables")

# Webhook settings
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE_URL')}{WEBHOOK_PATH}"
