import sqlite3
from typing import Optional, Type


class DatabaseConnection:
    """Custom context manager for handling SQLite database connections."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> sqlite3.Cursor:
        self._connection = sqlite3.connect(self.db_path)
        self._cursor = self._connection.cursor()
        return self._cursor

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb,
    ) -> bool:
        if self._cursor is not None:
            self._cursor.close()

        if self._connection is not None:
            if exc_type is not None:
                self._connection.rollback()
            else:
                self._connection.commit()
            self._connection.close()

        # Propagate exceptions, if any.
        return False


with DatabaseConnection("users.db") as cursor:
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

for row in rows:
    print(row)

