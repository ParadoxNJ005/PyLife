from modules.database import get_connection
from datetime import date


def add_dummy_data():
    print("🚀 Adding dummy data...")
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime("%Y-%m-%d")

    try:
        # 1. Add Friends (IGNORE means skip if they already exist)
        print("   - Adding friends: Pratham, Mokshhe")
        cursor.execute("INSERT OR IGNORE INTO friends (name) VALUES (?)", ("Pratham",))
        cursor.execute("INSERT OR IGNORE INTO friends (name) VALUES (?)", ("Mokshhe",))

        # Get their IDs for the debt records
        cursor.execute("SELECT id FROM friends WHERE name='Pratham'")
        pratham_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM friends WHERE name='Mokshhe'")
        mokshhe_id = cursor.fetchone()[0]

        # 2. Add YOUR Expense (Gupta-pparanthe, 90, Unhealthy=0)
        # Note: We assume '0' for unhealthy. Change to '1' if you think it's healthy.
        print("   - Logging expense: Gupta-pparanthe (₹90)")
        cursor.execute('''
            INSERT INTO expenses (date, item, amount, category, is_healthy)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, "gupta-pparanthe", 90, "Food", 0))

        # 3. Add Debts (They owe you 90 each)
        # lender_id = 0 represents 'Me' (the user)
        print("   - Logging debts: Pratham & Mokshhe owe ₹90 each")
        cursor.execute('''
            INSERT INTO debts (date, borrower_id, lender_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, pratham_id, 0, 90, "gupta-pparanthe split"))

        cursor.execute('''
            INSERT INTO debts (date, borrower_id, lender_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, mokshhe_id, 0, 90, "gupta-pparanthe split"))

        conn.commit()
        print("\n✅ Success! Data added to database.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    add_dummy_data()