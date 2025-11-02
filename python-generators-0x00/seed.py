import csv
import uuid
import mysql.connector
from mysql.connector import Error

# ================================
# DATABASE CONNECTION HELPERS
# ================================

def connect_db():
    """Connecting to the MySQL server."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",        
            password="1234"  
        )
        if connection.is_connected():
            print("Connected to MySQL server.")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def create_database(connection):
    """Create ALX_prodev db if it does not exist."""
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
    connection.commit()
    print("Database ALX_prodev ensured.")
    cursor.close()


def connect_to_prodev():
    """Connects directly to ALX_prodev db."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="ALX_prodev"
        )
        if connection.is_connected():
            print("Connected to ALX_prodev database.")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def create_table(connection):
    """Creates the user_data table if it doesn't exist."""
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX idx_user_id (user_id)
        );
    """)
    connection.commit()
    print("Table user_data ensured.")
    cursor.close()


def insert_data(connection, csv_file):
    """Reads data from a CSV file and inserts into user_data table if not already present."""
    cursor = connection.cursor()
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            name, email, age = row
            user_id = str(uuid.uuid4())
            cursor.execute("SELECT COUNT(*) FROM user_data WHERE email = %s;", (email,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s);
                """, (user_id, name, email, age))
    connection.commit()
    cursor.close()
    print("CSV data inserted successfully (if not already present).")


# ================================
# DATA STREAMING GENERATOR
# ================================

def stream_user_data(connection):
    """Generator that yields user_data rows one by one."""
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")
    for row in cursor:
        yield row
    cursor.close()


# ================================
# MAIN EXECUTION LOGIC
# ================================

if __name__ == "__main__":
    # Connecting to MySQL server
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()

    # Connecting to the specific database
    db_conn = connect_to_prodev()
    if db_conn:
        create_table(db_conn)

        # Reading CSV and insert data
        with open("user_data.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            insert_data(db_conn, list(reader))

        # Step 4: Stream rows using generator
        print("\nStreaming rows one by one:\n")
        for record in stream_user_data(db_conn):
            print(record)

        db_conn.close()
