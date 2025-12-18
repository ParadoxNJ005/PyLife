import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date

# --- 1. CONFIGURATION & SETUP ---
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env file.")

supabase: Client = create_client(url, key)


# --- 2. HELPER FUNCTIONS ---

def normalize_name(name):
    """Standardizes text to lowercase/stripped for comparison."""
    if not name: return ""
    return str(name).strip().lower()


def get_friend_id(name):
    """Resolves name to ID. Handles 'Me' -> Fetches 'Me' ID from DB."""
    clean_name = normalize_name(name)

    # Handle Self (User) keywords
    if clean_name in ["me", "i", "myself", "user", "self", "you"]:
        print(f"   -> Detected keyword '{name}', switching search to 'Me'...")
        clean_name = normalize_name("Me")

    # Query Database
    try:
        response = supabase.table("friends").select("id, name").execute()
        for f in response.data:
            if normalize_name(f['name']) == clean_name:
                return f['id']
    except Exception as e:
        print(f"   -> Error looking up friend: {e}")

    return None


# --- 3. MAIN EXECUTION ---

if __name__ == "__main__":
    # Input Data
    transaction_data = {
        'payer': 'Vansh',  # The person paying (The Lender)
        'amount': 50,
        'receiver': 'Me',  # The person benefiting (The Borrower)
        'description': 'Lunch'  # Added a default description
    }

    print("\n--- 🚀 PROCESSING TRANSACTION ---")
    print(f"Raw Input: {transaction_data}\n")

    # Step A: Resolve Payer (Lender)
    print(f"1️⃣ Resolving Payer (Lender): {transaction_data['payer']}")
    lender_id = get_friend_id(transaction_data['payer'])
    print(f"   ✅ Resolved Lender ID: {lender_id}\n")

    # Step B: Resolve Receiver (Borrower)
    print(f"2️⃣ Resolving Receiver (Borrower): {transaction_data['receiver']}")
    borrower_id = get_friend_id(transaction_data['receiver'])
    print(f"   ✅ Resolved Borrower ID: {borrower_id}\n")

    # Step C: Save to Database
    if lender_id and borrower_id:
        print("3️⃣ IDs found. Attempting to save to database...")

        try:
            # Prepare the record using YOUR database column names
            final_record = {
                "lender_id": lender_id,  # Vansh (13)
                "borrower_id": borrower_id,  # Me (11)
                "amount": transaction_data['amount'],
                "description": transaction_data.get('description', 'General'),
                "date": str(date.today()),  # Adds today's date like "2023-10-27"
                "status": "Active"  # Sets default status
            }

            print(f"   -> Payload: {final_record}")

            # INSERT into 'debts' table
            response = supabase.table("debts").insert(final_record).execute()

            print("\n🎉 SUCCESS! Transaction saved.")
            print(f"Database Response: {response.data}")

        except Exception as e:
            print(f"\n❌ FAILED to save to database: {e}")

    else:
        print("\n❌ ABORTED: Could not find ID for one or both users.")