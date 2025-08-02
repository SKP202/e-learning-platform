import psycopg2
import psycopg2.extras

DB_HOST = 'localhost'
DB_NAME = 'users'
DB_USER = 'postgres'
DB_PASS = 'superuser'

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return None