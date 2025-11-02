import mysql.connector
from mysql.connector import Error

def connect_to_prodev():
    """Connects to the ALX_prodev MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          
            password="your_password",
            database="ALX_prodev"
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def stream_users_in_batches(batch_size):
    """
    Generator that streams users from user_data table in batches.
    Yields each batch as a list of dicts.
    """
    connection = connect_to_prodev()
    if not connection:
        return

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch 

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """
    Processes batches of users and prints those older than 25.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
