import sqlite3
from typing import Iterable, Optional, Sequence, Type


class ExecuteQuery:
    """Context manager that executes a SQL query and returns its results."""

    def __init__(self, db_path: str, query: str, params: Sequence):
        self.db_path = db_path
        self.query = query
        self.params = params
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> Iterable:
        self._connection = sqlite3.connect(self.db_path)
        self._cursor = self._connection.cursor()
        self._cursor.execute(self.query, self.params)
        return self._cursor.fetchall()

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


QUERY = "SELECT * FROM users WHERE age > ?"
PARAMS = (25,)

with ExecuteQuery("users.db", QUERY, PARAMS) as rows:
    for row in rows:
        print(row)

