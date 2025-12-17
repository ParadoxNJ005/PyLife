import os
from dotenv import load_dotenv
from supabase import create_client


def fetch_total_owed(borrower_search: str = "Pratham"):
    """
    Fetch total owed amount for borrowers matching borrower_search
    where lender is 'Me' and debt status is Active.
    """
    # Load environment variables
    load_dotenv()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Service Role Key

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing Supabase environment variables")

    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # SQL query
    query = f"""
    SELECT 
        borrower.name,
        SUM(debts.amount) - COALESCE(SUM(payments.amount), 0) AS total_owed
    FROM debts
    JOIN friends AS borrower ON borrower.id = debts.borrower_id
    JOIN friends AS lender ON lender.id = debts.lender_id
    LEFT JOIN payments ON payments.debt_id = debts.id
    WHERE lender.name = 'Me'
        AND borrower.name ILIKE '%{borrower_search}%'
        AND debts.status = 'Active'
    GROUP BY borrower.name
    """

    # Execute query via RPC
    response = supabase.rpc("execute_sql", {"query": query}).execute()

    if response.data is None:
        raise RuntimeError(f"Query failed: {response}")

    return response.data


if __name__ == "__main__":
    try:
        results = fetch_total_owed("Pratham")

        if results:
            for row in results:
                print(f"Borrower: {row['name']}, Total Owed: {row['total_owed']}")
        else:
            print("No results found")

    except Exception as e:
        print("Error:", e)
