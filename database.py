import asyncpg
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bozorlik:bozorlik@localhost:5432/bozorlik")

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                name TEXT,
                family_size INTEGER DEFAULT 2,
                weekly_budget FLOAT DEFAULT 0,
                language TEXT DEFAULT 'uz',
                preferences TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT,
                meal_name TEXT,
                ingredients TEXT,
                recipe TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)


async def get_or_create_user(telegram_id: int, name: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (telegram_id, name) VALUES ($1, $2) ON CONFLICT (telegram_id) DO NOTHING",
            telegram_id, name
        )
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1", telegram_id
        )


async def update_language(telegram_id: int, lang: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET language = $1 WHERE telegram_id = $2",
            lang, telegram_id
        )


async def get_language(telegram_id: int) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT language FROM users WHERE telegram_id = $1", telegram_id
        )
        return row["language"] if row else "uz"


async def update_family_size(telegram_id: int, size: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET family_size = $1 WHERE telegram_id = $2",
            size, telegram_id
        )


async def save_shopping_list(telegram_id: int, meal_name: str, ingredients: str, recipe: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO shopping_lists (telegram_id, meal_name, ingredients, recipe) VALUES ($1, $2, $3, $4)",
            telegram_id, meal_name, ingredients, recipe
        )


async def get_last_shopping_list(telegram_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT meal_name, ingredients FROM shopping_lists WHERE telegram_id = $1 ORDER BY created_at DESC LIMIT 1",
            telegram_id
        )


async def get_user_history(telegram_id: int, limit: int = 5):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT meal_name, created_at FROM shopping_lists WHERE telegram_id = $1 ORDER BY created_at DESC LIMIT $2",
            telegram_id, limit
        )


async def update_weekly_budget(telegram_id: int, budget: float):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET weekly_budget = $1 WHERE telegram_id = $2",
            budget, telegram_id
        )


async def get_weekly_budget(telegram_id: int) -> float:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT weekly_budget FROM users WHERE telegram_id = $1", telegram_id
        )
        return row["weekly_budget"] if row else 0


async def get_family_size(telegram_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT family_size FROM users WHERE telegram_id = $1", telegram_id
        )
        return row["family_size"] if row else 2


async def update_preferences(telegram_id: int, preferences: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET preferences = $1 WHERE telegram_id = $2",
            preferences, telegram_id
        )


async def get_user_profile(telegram_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT family_size, weekly_budget, language, preferences FROM users WHERE telegram_id = $1",
            telegram_id
        )
        if row:
            return {
                "family_size": row["family_size"],
                "weekly_budget": row["weekly_budget"],
                "language": row["language"],
                "preferences": json.loads(row["preferences"] or "[]")
            }
        return {"family_size": 2, "weekly_budget": 0, "language": "uz", "preferences": []}


# --- Admin functions ---

async def get_all_users(limit: int = 50, offset: int = 0):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, telegram_id, name, family_size, weekly_budget, language, created_at FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit, offset
        )
        return [dict(r) for r in rows]


async def get_users_count() -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")


async def get_stats() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_lists = await conn.fetchval("SELECT COUNT(*) FROM shopping_lists")
        today_users = await conn.fetchval(
            "SELECT COUNT(DISTINCT telegram_id) FROM shopping_lists WHERE created_at >= CURRENT_DATE"
        )
        new_today = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE"
        )
        return {
            "total_users": total_users,
            "total_lists": total_lists,
            "active_today": today_users,
            "new_today": new_today,
        }


async def get_recent_lists(limit: int = 20, offset: int = 0):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT sl.id, sl.telegram_id, u.name, sl.meal_name, sl.created_at
               FROM shopping_lists sl
               LEFT JOIN users u ON sl.telegram_id = u.telegram_id
               ORDER BY sl.created_at DESC
               LIMIT $1 OFFSET $2""",
            limit, offset
        )
        return [dict(r) for r in rows]


async def delete_user(telegram_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM shopping_lists WHERE telegram_id = $1", telegram_id)
        await conn.execute("DELETE FROM users WHERE telegram_id = $1", telegram_id)
