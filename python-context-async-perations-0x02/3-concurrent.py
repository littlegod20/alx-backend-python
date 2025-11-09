import asyncio
import aiosqlite
from typing import List, Tuple

DB_PATH = "users.db"


async def async_fetch_users() -> List[Tuple]:
    """Fetch all users asynchronously."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


AGE_THRESHOLD = 40


async def async_fetch_older_users() -> List[Tuple]:
    """Fetch users older than the provided age threshold."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM users WHERE age > ?", (AGE_THRESHOLD,)
        ) as cursor:
            return await cursor.fetchall()


async def fetch_concurrently() -> None:
    """Run user queries concurrently and print the results."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
    )

    print("All users:")
    for user in all_users:
        print(user)

    print("\nUsers older than 40:")
    for user in older_users:
        print(user)


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())

