import asyncio
import aiosqlite
from typing import List, Tuple

DB_PATH = "users.db"


async def async_fetch_users(db_path: str) -> List[Tuple]:
    """Fetch all users asynchronously."""
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users(db_path: str, age_threshold: int = 40) -> List[Tuple]:
    """Fetch users older than the provided age threshold."""
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT * FROM users WHERE age > ?", (age_threshold,)
        ) as cursor:
            return await cursor.fetchall()


async def fetch_concurrently() -> None:
    """Run user queries concurrently and print the results."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(DB_PATH),
        async_fetch_older_users(DB_PATH),
    )

    print("All users:")
    for user in all_users:
        print(user)

    print("\nUsers older than 40:")
    for user in older_users:
        print(user)


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())

