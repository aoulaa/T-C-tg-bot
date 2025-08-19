# db/database.py

import aiosqlite
from datetime import datetime

DATABASE = 'tc_bot.db'

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS accepted_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                timestamp TEXT NOT NULL,
                t_and_c_version TEXT NOT NULL
            )
        ''')
        await db.commit()

async def add_user_acceptance(user_id: int, username: str, t_and_c_version: str):
    timestamp = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            'INSERT OR IGNORE INTO accepted_users (user_id, username, timestamp, t_and_c_version) VALUES (?, ?, ?, ?)',
            (user_id, username, timestamp, t_and_c_version)
        )
        await db.commit()
