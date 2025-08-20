import aiosqlite
from datetime import datetime

from config import DATABASE_NAME


async def init_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS accepted_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                username TEXT,
                timestamp TEXT NOT NULL,
                t_and_c_version TEXT NOT NULL,
                t_and_c_content TEXT NOT NULL,
                UNIQUE(user_id, chat_id)
            )
        ''')
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                chat_title TEXT,
                voice_only_mode TEXT DEFAULT 'off'
            )
        """)
        await db.commit()

async def add_user_acceptance(user_id: int, chat_id: int, username: str, t_and_c_version: str, t_and_c_content: str):
    timestamp = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            'INSERT OR IGNORE INTO accepted_users (user_id, chat_id, username, timestamp, t_and_c_version, t_and_c_content) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, chat_id, username, timestamp, t_and_c_version, t_and_c_content)
        )
        await db.commit()

async def set_voice_only_mode(chat_id: int, chat_title: str, mode: str):
    """Sets the voice-only mode for a given chat and records its title."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            "INSERT INTO group_settings (chat_id, chat_title, voice_only_mode) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET voice_only_mode = excluded.voice_only_mode, chat_title = excluded.chat_title",
            (chat_id, chat_title, mode)
        )
        await db.commit()

async def get_voice_only_mode(chat_id: int) -> str:
    """Gets the voice-only mode for a given chat."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute("SELECT voice_only_mode FROM group_settings WHERE chat_id = ?", (chat_id,))
        result = await cursor.fetchone()
        return result[0] if result else 'off'

async def get_all_user_acceptances() -> list:
    """Retrieves all records from the accepted_users table."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id, chat_id, username, t_and_c_version, t_and_c_content, timestamp FROM accepted_users ORDER BY timestamp DESC")
        rows = await cursor.fetchall()
        return rows


async def get_all_group_settings() -> list:
    """Retrieves all records from the group_settings table."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT chat_id, chat_title, voice_only_mode FROM group_settings")
        rows = await cursor.fetchall()
        return rows
