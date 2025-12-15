import sqlite3
import os

# Define the path to the database file
# --- PATH CONFIGURATION ---
# Get the directory where THIS file (database.py) is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the Project Root
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
# Define the data folder and DB file paths
DB_FOLDER = os.path.join(PROJECT_ROOT, 'data')
DB_FILE = os.path.join(DB_FOLDER, 'tracker.db')

def get_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure the data folder exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    conn = sqlite3.connect(DB_FILE)
    # This allows us to access columns by name (row['id']) instead of index (row[0])
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Creates the necessary tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Create FRIENDS Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT
    )
    ''')

    # 2. Create EXPENSES Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        item TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        is_healthy BOOLEAN
    )
    ''')

    # 3. Create DEBTS Table (Tracks the original borrowing event)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS debts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        borrower_id INTEGER NOT NULL,
        lender_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'Active',
        FOREIGN KEY (borrower_id) REFERENCES friends (id),
        FOREIGN KEY (lender_id) REFERENCES friends (id)
    )
    ''')

    # 4. Create PAYMENTS Table (Tracks paybacks)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        debt_id INTEGER NOT NULL,
        payer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (debt_id) REFERENCES debts (id),
        FOREIGN KEY (payer_id) REFERENCES friends (id)
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at: {DB_FILE}")


# Helper function to run simple queries safely
# Updated Helper function
# Helper function to run simple queries safely
def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
        return None
    finally:
        conn.close()


# If this file is run directly, initialize the DB
if __name__ == "__main__":
    initialize_db()