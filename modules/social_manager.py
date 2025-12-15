import sqlite3
from datetime import date
from modules.database import get_connection


def get_friend_id(name):
    """Helper function: Resolves a name (string) to a Database ID (int)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM friends WHERE name = ? COLLATE NOCASE", (name.strip(),))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None


def add_friend(name, phone=None):
    """Adds a new friend to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO friends (name, phone) VALUES (?, ?)", (name.strip(), phone))
        conn.commit()
        print(f"✅ Friend added: {name}")
        return f"Added {name}"
    except sqlite3.IntegrityError:
        print(f"❌ Error: Friend '{name}' already exists.")
        return "Duplicate Error"
    finally:
        conn.close()


def list_friends():
    """Returns a list of all friends currently in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone FROM friends")
    rows = cursor.fetchall()
    conn.close()

    # Convert database rows to a simple list of strings
    friend_list = [row['name'] for row in rows]
    return friend_list


def log_debt(borrower_name, lender_name, amount, description="General Loan"):
    """Records a debt between two friends."""
    borrower_id = get_friend_id(borrower_name)
    lender_id = get_friend_id(lender_name)

    if not borrower_id or not lender_id:
        print("❌ Error: One or both friends not found. Please use 'add_friend' first.")
        return "Error: Unknown Friend"

    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime("%Y-%m-%d")

    cursor.execute('''
        INSERT INTO debts (date, borrower_id, lender_id, amount, description, status)
        VALUES (?, ?, ?, ?, ?, 'Active')
    ''', (today, borrower_id, lender_id, amount, description))

    conn.commit()
    conn.close()
    print(f"✅ Debt Logged: {borrower_name} owes {lender_name} ${amount} for '{description}'")
    return "Success"


def record_payment(payer_name, receiver_name, payment_amount):
    """
    Records a payment.
    Smart Logic: Automatically finds active debts between these two people
    and applies the payment to the OLDEST debt first.
    """
    payer_id = get_friend_id(payer_name)
    receiver_id = get_friend_id(receiver_name)

    if not payer_id or not receiver_id:
        print("❌ Error: Friend not found.")
        return "Error"

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Find all 'Active' debts where the Payer owes the Receiver
    # Ordered by ID asc (Oldest first)
    cursor.execute('''
        SELECT id, amount FROM debts 
        WHERE borrower_id = ? AND lender_id = ? AND status = 'Active'
        ORDER BY id ASC
    ''', (payer_id, receiver_id))

    active_debts = cursor.fetchall()

    remaining_payment = float(payment_amount)
    today = date.today().strftime("%Y-%m-%d")

    if not active_debts:
        print(f"⚠️ No active debts found for {payer_name} -> {receiver_name}. Payment recorded as overpayment/credit.")
        # In a real app, you might store this as a positive credit.
        # For now, we just log it as a generic payment linked to ID 0 or NULL to keep it simple.
        return "No Active Debts"

    for debt in active_debts:
        if remaining_payment <= 0:
            break

        debt_id = debt['id']
        debt_amount = debt['amount']

        # Calculate how much we have already paid for this specific debt
        cursor.execute("SELECT SUM(amount) as paid FROM payments WHERE debt_id = ?", (debt_id,))
        already_paid = cursor.fetchone()['paid'] or 0.0

        balance_due = debt_amount - already_paid

        # Determine how much of the current payment goes to this debt
        pay_chunk = min(remaining_payment, balance_due)

        # Log the payment chunk
        cursor.execute('''
            INSERT INTO payments (date, debt_id, payer_id, amount)
            VALUES (?, ?, ?, ?)
        ''', (today, debt_id, payer_id, pay_chunk))

        # Check if this specific debt is now fully paid
        if (already_paid + pay_chunk) >= debt_amount:
            cursor.execute("UPDATE debts SET status = 'Settled' WHERE id = ?", (debt_id,))
            print(f"🎉 Debt #{debt_id} is now SETTLED!")

        remaining_payment -= pay_chunk

    conn.commit()
    conn.close()
    print(f"✅ Payment recorded: {payer_name} paid {receiver_name} ${payment_amount}")
    return "Success"