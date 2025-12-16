import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from supabase import create_client

# --- 1. SETUP SUPABASE CONNECTION ---
# Load environment variables
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Stop if credentials are missing
if not url or not key:
    st.error("❌ Supabase credentials missing. Please check your .env file.")
    st.stop()

# Initialize Client
try:
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.stop()


# --- 2. LOAD DATA FUNCTIONS ---
def load_data():
    """Fetches Expenses, Debts, and Friends from Supabase"""

    # A. Fetch Expenses
    response_exp = supabase.table("expenses").select("*").execute()
    df_expenses = pd.DataFrame(response_exp.data)

    # B. Fetch Debts & Friends (to get names instead of IDs)
    response_debts = supabase.table("debts").select("*").execute()
    response_friends = supabase.table("friends").select("id, name").execute()

    df_debts = pd.DataFrame(response_debts.data)
    df_friends = pd.DataFrame(response_friends.data)

    # C. Merge Friend Names into Debts
    # We do this merge in Python because Supabase API joins are more complex
    if not df_debts.empty and not df_friends.empty:
        # Join 'debts' and 'friends' on borrower_id = id
        df_debts = df_debts.merge(df_friends, left_on='borrower_id', right_on='id', how='left')
        df_debts.rename(columns={'name': 'borrower_name'}, inplace=True)

    return df_expenses, df_debts


# --- 3. DASHBOARD LAYOUT ---
st.set_page_config(page_title="FiscalFit Cloud", page_icon="☁️", layout="wide")

st.title("☁️ FiscalFit: Cloud Dashboard")
st.markdown("---")

# Refresh Button
if st.button('🔄 Refresh Cloud Data'):
    st.rerun()

# Load Data
with st.spinner("Fetching data from cloud..."):
    df_expenses, df_debts = load_data()

# Check if we have data
if df_expenses.empty:
    st.warning("No expenses found in the cloud yet. Try logging some using the CLI or Agent!")
else:
    # --- 4. TOP METRICS ROW ---
    # Convert string dates to datetime objects for sorting
    df_expenses['date'] = pd.to_datetime(df_expenses['date'])

    # Calculate Total Spent
    total_spent = df_expenses['amount'].sum()

    # Calculate Health Score
    # Count items where is_healthy is True
    healthy_count = df_expenses[df_expenses['is_healthy'] == True].shape[0]
    total_items = df_expenses.shape[0]
    health_score = int((healthy_count / total_items) * 100) if total_items > 0 else 0

    # Calculate Active Debt (Money people owe you)
    total_owed = 0
    if not df_debts.empty and 'status' in df_debts.columns:
        total_owed = df_debts[df_debts['status'] == 'Active']['amount'].sum()

    # Display Columns
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
    col2.metric("🍎 Health Score", f"{health_score}% Healthy")
    col3.metric("🤝 Friends Owe You", f"₹{total_owed:,.2f}")

    st.markdown("---")

    # --- 5. CHARTS ROW ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🥗 Healthy vs Unhealthy")
        if 'is_healthy' in df_expenses.columns:
            # Create a copy to map True/False to text labels
            df_health = df_expenses.copy()
            df_health['Health Status'] = df_health['is_healthy'].map({True: 'Healthy', False: 'Unhealthy'})

            # Pie Chart
            fig_pie = px.pie(df_health, names='Health Status', values='amount',
                             color='Health Status',
                             color_discrete_map={'Healthy': '#2ecc71', 'Unhealthy': '#e74c3c'})
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("📅 Spending Trend")
        # Group by date and sum amounts
        daily_spend = df_expenses.groupby('date')['amount'].sum().reset_index()
        # Line Chart
        fig_line = px.line(daily_spend, x='date', y='amount', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

    # --- 6. DATA TABLES ---
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("📜 Recent Cloud Logs")
        # Show specific columns, sorted by newest first
        st.dataframe(
            df_expenses[['date', 'item', 'amount', 'category']].sort_values(by='date', ascending=False),
            use_container_width=True,
            height=300
        )

    with c4:
        st.subheader("📒 Active Debt Log")
        if not df_debts.empty and 'status' in df_debts.columns:
            active_debts = df_debts[df_debts['status'] == 'Active']
            if not active_debts.empty:
                st.dataframe(
                    active_debts[['date', 'borrower_name', 'amount', 'description']],
                    use_container_width=True
                )
            else:
                st.success("No active debts! Everyone is settled up.")
        else:
            st.info("No debt records found in the cloud.")