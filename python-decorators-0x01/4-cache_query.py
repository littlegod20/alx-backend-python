import time
import sqlite3 
import functools


query_cache = {}

def cache_query(func):
    """Cache query results based on the SQL query string."""

    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get("query")
        if query is None:
            if args:
                query = args[0]
            else:
                return func(conn, *args, **kwargs)

        if query in query_cache:
            return query_cache[query]

        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        return result

    return wrapper

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        result = func(conn, *args, **kwargs)
        conn.close()
        return result
    return wrapper

    
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")