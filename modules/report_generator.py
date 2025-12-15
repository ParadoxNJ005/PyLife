import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from modules.database import get_connection

# Define output folder for graphs
GRAPH_FOLDER = os.path.join('reports', 'graphs')
if not os.path.exists(GRAPH_FOLDER):
    os.makedirs(GRAPH_FOLDER)


def generate_monthly_report(month=None, year=None):
    """
    Generates a report for a specific month.
    If no month is provided, defaults to the current month.
    """
    # Default to current date if not specified
    now = datetime.now()
    if month is None: month = now.month
    if year is None: year = now.year

    # Format 'YYYY-MM' for SQL filtering
    month_str = f"{year}-{month:02d}"
    print(f"\n📊 --- Generating Report for {month_str} ---")

    conn = get_connection()

    # 1. FETCH DATA using Pandas
    query = "SELECT date, item, amount, category, is_healthy FROM expenses WHERE date LIKE ?"
    df = pd.read_sql_query(query, conn, params=(f"{month_str}%",))
    conn.close()

    if df.empty:
        print("❌ No data found for this month.")
        return "No Data"

    # --- PART A: THE DATA TABLES ---

    # Summary by Category
    category_summary = df.groupby('category')['amount'].sum().sort_values(ascending=False)

    # Summary by Health (Mapping 1/0 to 'Healthy'/'Unhealthy')
    df['health_label'] = df['is_healthy'].map({1: 'Healthy', 0: 'Unhealthy'})
    health_summary = df.groupby('health_label')['amount'].sum()

    print("\n💰 EXPENSE BREAKDOWN (Data Table):")
    print(category_summary.to_string())
    print(f"\nTotal Spent: ${df['amount'].sum():.2f}")

    # --- PART B: THE GRAPHS ---

    # Graph 1: Spending by Category (Bar Chart)
    plt.figure(figsize=(10, 6))
    category_summary.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f'Expenses by Category ({month_str})')
    plt.ylabel('Amount ($)')
    plt.xlabel('Category')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save Graph 1
    cat_graph_path = os.path.join(GRAPH_FOLDER, f"expense_category_{month_str}.png")
    plt.savefig(cat_graph_path)
    print(f"\n📈 Category Graph saved to: {cat_graph_path}")
    plt.close()

    # Graph 2: Health Breakdown (Pie Chart)
    if not health_summary.empty:
        plt.figure(figsize=(6, 6))
        colors = ['#ff9999', '#66b3ff']  # Red for unhealthy, Blue for healthy (approx)
        health_summary.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title(f'Health Audit ({month_str})')
        plt.ylabel('')  # Hide y-label

        # Save Graph 2
        health_graph_path = os.path.join(GRAPH_FOLDER, f"health_audit_{month_str}.png")
        plt.savefig(health_graph_path)
        print(f"🍏 Health Graph saved to: {health_graph_path}")
        plt.close()

    return {
        "total_spent": df['amount'].sum(),
        "graphs": [cat_graph_path, health_graph_path]
    }