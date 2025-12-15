import json
import os
import sqlite3
from datetime import date
from modules.database import get_connection

# --- HELPER: JSON HEALTH DATA ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
JSON_FILE = os.path.join(PROJECT_ROOT, 'data', 'item_health.json')


def load_health_data():
    if not os.path.exists(JSON_FILE): return {}
    with open(JSON_FILE, 'r') as f: return json.load(f)


def save_health_data(data):
    with open(JSON_FILE, 'w') as f: json.dump(data, f, indent=4)


def check_item_health(item):
    data = load_health_data()
    return data.get(item.lower().strip(), None)


def learn_item_health(item, is_healthy):
    data = load_health_data()
    data[item.lower().strip()] = is_healthy
    save_health_data(data)


# --- CORE FUNCTIONS ---

def get_or_create_friend(name):
    """Finds a friend's ID or creates them if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Try to find friend
        cursor.execute("SELECT id FROM friends WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row:
            return row['id']

        # 2. If not found, create new friend
        cursor.execute("INSERT INTO friends (name) VALUES (?)", (name,))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def log_expense(item, amount, category="Food", is_healthy=None):
    """Logs a personal expense."""
    # 1. Health Check
    if is_healthy is None:
        known_status = check_item_health(item)
        if known_status is None:
            return {"status": "NEEDS_CLARIFICATION", "item": item, "amount": amount}
        is_healthy = known_status

    # 2. DB Insert
    conn = get_connection()
    cursor = conn.cursor()
    try:
        today = date.today().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO expenses (date, item, amount, category, is_healthy)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, item, amount, category, 1 if is_healthy else 0))
        conn.commit()
        return {"status": "SUCCESS", "message": f"Logged {item} (₹{amount})"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
    finally:
        conn.close()


def log_debt(lender, borrower, amount, description):
    """Logs a debt between two people (e.g., Me -> Pratham)."""
    try:
        borrower_id = get_or_create_friend(borrower)

        conn = get_connection()
        cursor = conn.cursor()
        today = date.today().strftime("%Y-%m-%d")

        # Note: You might need to adjust logic if 'lender' is 'me' vs a friend
        cursor.execute('''
            INSERT INTO debts (date, borrower_id, lender_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, borrower_id, 0, amount, description))  # 0 = User/Me

        conn.commit()
        conn.close()
        return {"status": "SUCCESS", "message": f"Recorded: {borrower} owes ₹{amount} for {description}"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}