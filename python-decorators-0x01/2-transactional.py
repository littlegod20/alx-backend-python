import sqlite3
import functools

"""Decorator for wrapping database operations in a transaction."""


def transactional(func):
    """Ensure the wrapped function runs within a transaction."""

    @functools.wraps(func)
    def wrapper(conn: sqlite3.Connection, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
            return result

    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")