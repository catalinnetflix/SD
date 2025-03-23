
import psycopg2

DB_NAME = "postgres"
USER = "postgres"
PASSWORD = "cata"
HOST = "localhost"
PORT = "5432"

def setup_database():
    conn = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            filepath TEXT UNIQUE,
            filename TEXT,
            content TEXT,
            extension TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
