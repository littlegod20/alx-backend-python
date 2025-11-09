import sqlite3
import functools
from datetime import datetime


def log_queries(func):
    """Decorator that logs SQL queries before executing them."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = args[0] if args else kwargs.get("query", "")
        timestamp = datetime.now().isoformat(timespec="seconds")
        print(f"[{timestamp}] Executing query: {query}")
        return func(*args, **kwargs)

    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")