import sqlite3

DATABASE = "ddos_data.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with get_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS ddos_data (
            saddr TEXT PRIMARY KEY,
            total_dur REAL,
            count INTEGER
        )
        ''')
