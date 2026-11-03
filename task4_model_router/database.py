import time
from pathlib import Path

import aiosqlite


DATABASE_PATH = Path(__file__).with_name("usage.db")
TOKEN_LIMIT = 50_000
WINDOW_SECONDS = 60


async def initialize_database():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                tokens INTEGER NOT NULL CHECK(tokens > 0),
                created_at REAL NOT NULL
            )
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tenant_created
            ON token_usage(tenant_id, created_at)
        """)

        await db.commit()


async def reserve_tokens(
    tenant_id: str,
    tokens: int,
    limit: int = TOKEN_LIMIT,
) -> dict:
    if not tenant_id:
        raise ValueError("Tenant ID is required")

    if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens <= 0:
        raise ValueError("Token count must be a positive integer")

    now = time.time()
    window_start = now - WINDOW_SECONDS

    async with aiosqlite.connect(
        DATABASE_PATH,
        isolation_level=None,
    ) as db:

        try:
            # Serialize concurrent writers to prevent limit bypass.
            await db.execute("BEGIN IMMEDIATE")

            # Remove expired usage records.
            await db.execute(
                "DELETE FROM token_usage WHERE created_at <= ?",
                (window_start,),
            )

            # Calculate this tenant's usage in the last 60 seconds.
            cursor = await db.execute(
                """
                SELECT COALESCE(SUM(tokens), 0)
                FROM token_usage
                WHERE tenant_id = ?
                  AND created_at > ?
                """,
                (tenant_id, window_start),
            )

            row = await cursor.fetchone()
            current_usage = row[0]

            if current_usage + tokens > limit:
                await db.commit()

                return {
                    "allowed": False,
                    "tenant_id": tenant_id,
                    "current_usage": current_usage,
                    "requested_tokens": tokens,
                    "limit": limit,
                    "remaining_tokens": max(0, limit - current_usage),
                }

            # Reserve tokens atomically.
            await db.execute(
                """
                INSERT INTO token_usage (tenant_id, tokens, created_at)
                VALUES (?, ?, ?)
                """,
                (tenant_id, tokens, now),
            )

            await db.commit()

            return {
                "allowed": True,
                "tenant_id": tenant_id,
                "current_usage": current_usage + tokens,
                "requested_tokens": tokens,
                "limit": limit,
                "remaining_tokens": limit - current_usage - tokens,
            }

        except Exception:
            await db.rollback()
            raise