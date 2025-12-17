import os
import psycopg2
from modules.database import get_client

# --- 1. THE BRAIN (Schema for the AI) ---
DB_SCHEMA = """
You are a Data Analyst. Convert the user's question into a specific SQL query for PostgreSQL.

TABLES:
1. friends (id, name, phone)
   - Contains all people, including the user ('Me').

2. expenses (id, date, item, amount, category, is_healthy)
   - 'is_healthy' is boolean (true/false).
   - 'date' is YYYY-MM-DD.

3. item_health (id, item, is_healthy)
   - A knowledge base of which items are healthy/unhealthy.

4. debts (id, date, borrower_id, lender_id, amount, description, status)
   - 'borrower_id' links to friends.id (The person OWING money).
   - 'lender_id' links to friends.id (The person GIVING money).
   - 'status' is usually 'Active' or 'Settled'.

5. payments (id, date, debt_id, payer_id, amount)
   - 'debt_id' links to debts.id.
   - Payments reduce the specific debt amount.

CRITICAL RULES:
1. Return ONLY the raw SQL. No markdown (```sql), no explanations.
2. Do not use DELETE, DROP, or UPDATE. Read-only queries only.
3. IDENTIFYING 'ME':
   - Do NOT assume the user's ID is 0.
   - To find the user, subquery the friends table: (SELECT id FROM friends WHERE name ILIKE 'Me')
   - Example: WHERE lender_id = (SELECT id FROM friends WHERE name ILIKE 'Me')

4. CALCULATING OWED AMOUNT:
   - To find "How much does Pratham owe Me?", use this logic:
     SELECT SUM(d.amount) - COALESCE(SUM(p.amount), 0)
     FROM debts d
     LEFT JOIN payments p ON d.id = p.debt_id
     WHERE d.lender_id = (SELECT id FROM friends WHERE name ILIKE 'Me')
     AND d.borrower_id = (SELECT id FROM friends WHERE name ILIKE '%Pratham%')
     AND d.status = 'Active';
"""


def run_raw_sql(query):
    """Executes raw SQL using psycopg2 (Direct DB Connection)."""
    conn = None
    try:
        # Connect using the string from .env
        db_url = os.getenv("DB_CONNECTION_STRING")
        if not db_url:
            return None, "❌ Error: DB_CONNECTION_STRING is missing from .env file."

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute(query)

        # If query is a SELECT, fetch data.
        if query.strip().upper().startswith("SELECT"):
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            return columns, results
        else:
            conn.commit()
            return [], "Action completed."

    except Exception as e:
        return None, f"SQL Error: {str(e)}"
    finally:
        if conn: conn.close()


def ask_database(user_question, ai_client_func):
    """
    1. Sends Schema + Question to AI.
    2. Runs generated SQL.
    3. Returns data.
    """
    print(f"🤔 Analyzing: {user_question}")

    # Step 1: Get SQL from AI
    prompt = f"{DB_SCHEMA}\n\nUser Question: {user_question}\nSQL Query:"

    # This calls your AI function
    sql_query = ai_client_func(prompt).strip()

    # Clean up markdown if the AI adds it
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    print(f"🤖 Generated SQL: {sql_query}")

    # Step 2: Run SQL using psycopg2 (Path B)
    # We use this instead of supabase-py to avoid the raw SQL limitation
    columns, data = run_raw_sql(sql_query)

    if isinstance(data, str) and ("Error" in data or "limitation" in data):
        return f"❌ Execution Failed: {data}"

    if not data:
        return "📭 Database returned no results."

    # Step 3: Format the Output
    result_str = f"**Results:**\n"
    for row in data:
        result_str += f"- {row}\n"

    return result_str