import aiosqlite

import os
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bozorlik.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                name TEXT,
                family_size INTEGER DEFAULT 2,
                weekly_budget REAL DEFAULT 0,
                language TEXT DEFAULT 'uz',
                preferences TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                meal_name TEXT,
                ingredients TEXT,
                recipe TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_or_create_user(telegram_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, name) VALUES (?, ?)",
            (telegram_id, name)
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()


async def update_language(telegram_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE telegram_id = ?",
            (lang, telegram_id)
        )
        await db.commit()


async def get_language(telegram_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT language FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "uz"


async def update_family_size(telegram_id: int, size: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET family_size = ? WHERE telegram_id = ?",
            (size, telegram_id)
        )
        await db.commit()


async def save_shopping_list(telegram_id: int, meal_name: str, ingredients: str, recipe: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO shopping_lists (telegram_id, meal_name, ingredients, recipe) VALUES (?, ?, ?, ?)",
            (telegram_id, meal_name, ingredients, recipe)
        )
        await db.commit()


async def get_last_shopping_list(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT meal_name, ingredients FROM shopping_lists WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 1",
            (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()


async def get_user_history(telegram_id: int, limit: int = 5):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT meal_name, created_at FROM shopping_lists WHERE telegram_id = ? ORDER BY created_at DESC LIMIT ?",
            (telegram_id, limit)
        ) as cursor:
            return await cursor.fetchall()


async def update_weekly_budget(telegram_id: int, budget: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET weekly_budget = ? WHERE telegram_id = ?",
            (budget, telegram_id)
        )
        await db.commit()


async def get_weekly_budget(telegram_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT weekly_budget FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_family_size(telegram_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT family_size FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 2


async def update_preferences(telegram_id: int, preferences: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET preferences = ? WHERE telegram_id = ?",
            (preferences, telegram_id)
        )
        await db.commit()


async def get_user_profile(telegram_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT family_size, weekly_budget, language, preferences FROM users WHERE telegram_id = ?",
            (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                import json
                return {
                    "family_size": row[0], "weekly_budget": row[1],
                    "language": row[2], "preferences": json.loads(row[3] or '[]')
                }
            return {"family_size": 2, "weekly_budget": 0, "language": "uz", "preferences": []}
