import sqlite3
import os
import pandas as pd
from datetime import date
from modules.database import get_connection

# --- CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
REPORTS_FOLDER = os.path.join(PROJECT_ROOT, 'reports')
EXCEL_FILE = os.path.join(REPORTS_FOLDER, 'data.xlsx')


def export_to_excel():
    """Fetches all data and saves it to reports/data.xlsx"""
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)

    conn = get_connection()
    try:
        # 1. Fetch Expenses
        df_expenses = pd.read_sql_query("SELECT * FROM expenses", conn)

        # 2. Fetch Debts
        query_debts = """
        SELECT d.id, d.date, f.name as borrower, d.amount, d.description, d.status 
        FROM debts d
        JOIN friends f ON d.borrower_id = f.id
        """
        df_debts = pd.read_sql_query(query_debts, conn)

        # 3. Write to Excel
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df_expenses.to_excel(writer, sheet_name='Expenses', index=False)
            df_debts.to_excel(writer, sheet_name='Debts', index=False)

        return f"📊 Excel file saved at: {EXCEL_FILE}"
    except Exception as e:
        return f"❌ Error generating Excel: {str(e)}"
    finally:
        conn.close()


def generate_monthly_report(month=None, year=None):
    """
    Generates the Excel file and returns a text summary for Claude.
    """
    # 1. Create the Excel File
    excel_status = export_to_excel()

    # 2. Build the Text Report
    conn = get_connection()
    cursor = conn.cursor()

    if month is None or year is None:
        today = date.today()
        month = today.month
        year = today.year

    # Filter by YYYY-MM
    date_pattern = f"{year}-{month:02d}%"
    output = []  # We will build the response string here

    output.append(f"--- 📅 Monthly Report for {month}/{year} ---")
    output.append(excel_status)  # Add the Excel confirmation line

    try:
        cursor.execute("SELECT amount, is_healthy FROM expenses WHERE date LIKE ?", (date_pattern,))
        rows = cursor.fetchall()

        total_spent = sum(r['amount'] for r in rows)
        healthy_spent = sum(r['amount'] for r in rows if r['is_healthy'])
        unhealthy_spent = sum(r['amount'] for r in rows if not r['is_healthy'])

        output.append(f"💰 Total Spent:   ₹{total_spent:,.2f}")
        output.append(f"🥗 Healthy:       ₹{healthy_spent:,.2f}")
        output.append(f"🍔 Unhealthy:     ₹{unhealthy_spent:,.2f}")

        if total_spent > 0:
            h_pct = (healthy_spent / total_spent) * 100
            output.append(f"📈 Diet Score:    {h_pct:.1f}% Healthy Spending")
        else:
            output.append("No expenses recorded for this month.")

    except sqlite3.Error as e:
        output.append(f"Database error: {e}")
    finally:
        conn.close()

    # Join list into a single string to send back to Claude
    return "\n".join(output)