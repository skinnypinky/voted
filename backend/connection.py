import psycopg

def get_db_connection():
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5433/voted")
    return conn