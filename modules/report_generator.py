import os
import pandas as pd
from datetime import date
from modules.database import get_client

# --- CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
REPORTS_FOLDER = os.path.join(PROJECT_ROOT, 'reports')
EXCEL_FILE = os.path.join(REPORTS_FOLDER, 'data.xlsx')


def export_to_excel():
    """Fetches all data from Supabase and saves it to reports/data.xlsx"""
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)

    supabase = get_client()
    try:
        # 1. Fetch Expenses (Cloud)
        exp_res = supabase.table("expenses").select("*").execute()
        df_expenses = pd.DataFrame(exp_res.data)

        # 2. Fetch Debts (Cloud)
        debt_res = supabase.table("debts").select("*").execute()

        # 3. Fetch Friends (Cloud) to resolve IDs -> Names
        friend_res = supabase.table("friends").select("id, name").execute()

        df_debts = pd.DataFrame(debt_res.data)
        df_friends = pd.DataFrame(friend_res.data)

        # Merge if data exists to replace IDs with Names
        if not df_debts.empty and not df_friends.empty:
            df_debts = df_debts.merge(df_friends, left_on='borrower_id', right_on='id', how='left')
            # Rename column for clarity
            df_debts.rename(columns={'name': 'borrower_name'}, inplace=True)
            # Cleanup: Drop extra ID columns if preferred (optional)
            if 'id_y' in df_debts.columns:
                df_debts.drop(columns=['id_y'], inplace=True)

        # 4. Write to Excel
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            if not df_expenses.empty:
                df_expenses.to_excel(writer, sheet_name='Expenses', index=False)
            else:
                # Create empty sheet if no data to avoid errors
                pd.DataFrame({'Message': ['No expenses found']}).to_excel(writer, sheet_name='Expenses', index=False)

            if not df_debts.empty:
                df_debts.to_excel(writer, sheet_name='Debts', index=False)
            else:
                pd.DataFrame({'Message': ['No debts found']}).to_excel(writer, sheet_name='Debts', index=False)

        return f"📊 Excel file saved at: {EXCEL_FILE}"
    except Exception as e:
        return f"❌ Error generating Excel: {str(e)}"


def generate_monthly_report(month=None, year=None):
    """
    Generates the Excel file locally and returns a text summary for the Agent.
    """
    # 1. Create the Excel File
    excel_status = export_to_excel()

    # 2. Build the Text Report
    if month is None or year is None:
        today = date.today()
        month = today.month
        year = today.year

    # Supabase Filtering
    # We construct a date range: Start of this month -> Start of next month
    start_date = f"{year}-{month:02d}-01"

    # Logic to get the first day of the next month
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    output = []
    output.append(f"--- 📅 Monthly Report for {month}/{year} ---")
    output.append(excel_status)

    try:
        supabase = get_client()

        # Filter: date >= start_date AND date < end_date
        response = supabase.table("expenses").select("*") \
            .gte("date", start_date) \
            .lt("date", end_date) \
            .execute()

        rows = response.data

        if not rows:
            output.append("No expenses recorded for this month.")
            return "\n".join(output)

        # Calculate Stats in Python
        total_spent = sum(float(r['amount']) for r in rows)
        healthy_spent = sum(float(r['amount']) for r in rows if r['is_healthy'] is True)
        unhealthy_spent = sum(float(r['amount']) for r in rows if r['is_healthy'] is False)

        output.append(f"💰 Total Spent:   ₹{total_spent:,.2f}")
        output.append(f"🥗 Healthy:       ₹{healthy_spent:,.2f}")
        output.append(f"🍔 Unhealthy:     ₹{unhealthy_spent:,.2f}")

        if total_spent > 0:
            h_pct = (healthy_spent / total_spent) * 100
            output.append(f"📈 Diet Score:    {h_pct:.1f}% Healthy Spending")

    except Exception as e:
        output.append(f"Cloud Error: {str(e)}")

    return "\n".join(output)