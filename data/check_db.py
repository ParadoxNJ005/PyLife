import sqlite3
import os

# 1. Define the database file name
# (Make sure this matches the filename inside modules/database.py)
DB_NAME = "tracker.db"

def view_data():
    if not os.path.exists(DB_NAME):
        print(f"❌ Database file '{DB_NAME}' not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # 2. Select all data from the expenses table
        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()

        if not rows:
            print("📭 Database exists but the table is empty.")
        else:
            print(f"\n{'Date':<12} {'Item':<20} {'Amount':<10} {'Healthy?':<10}")
            print("-" * 60)
            for row in rows:
                # Adjust indices [1], [2] etc based on your specific table columns
                # Typically: id, date, item, amount, category, is_healthy
                print(f"{row[1]:<12} {row[2]:<20} {row[3]:<10} {row[5]}")

    except sqlite3.Error as e:
        print(f"❌ SQL Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    view_data()