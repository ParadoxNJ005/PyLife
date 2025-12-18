from datetime import date
from modules.database import get_client


def normalize_name(name):
    """Standardize names to lowercase/stripped."""
    if not name: return ""
    return str(name).lower().strip()


def get_friend_id(name):
    """
    Resolves name to ID.
    Handles 'Me' -> Fetches the actual ID for 'Me' from the database.
    """
    clean_name = normalize_name(name)

    # 1. Handle Self (User) - Redirect to "Me"
    if clean_name in ["me", "i", "myself", "user", "self", "you"]:
        clean_name = normalize_name("Me")

    # 2. Query Database
    supabase = get_client()
    try:
        # Fetch all friends to find the matching name
        # Optimization: For large lists, we could use .ilike('name', clean_name)
        response = supabase.table("friends").select("id, name").execute()

        for f in response.data:
            if normalize_name(f['name']) == clean_name:
                return f['id']

    except Exception as e:
        print(f"❌ Error looking up friend: {e}")

    return None


def add_friend(name, phone=None):
    supabase = get_client()
    clean_name = name.strip()

    # Check if exists
    if get_friend_id(clean_name) is not None:
        return f"⚠️ Friend '{clean_name}' already exists."

    try:
        data = {"name": clean_name, "phone": phone}
        supabase.table("friends").insert(data).execute()
        return f"✅ Friend added: {clean_name}"

    except Exception as e:
        return f"❌ Error adding friend: {str(e)}"


def list_friends():
    supabase = get_client()
    try:
        res = supabase.table("friends").select("name").execute()
        return [f['name'] for f in res.data]
    except:
        return []


def log_debt(borrower_name, lender_name, amount, description="General Loan"):
    try:
        print(f"Processing Debt: '{borrower_name}' owes '{lender_name}'")

        # --- RESOLVE IDS ---
        # No more hardcoded 0. We ask the database for the IDs.
        lender_id = get_friend_id(lender_name)
        borrower_id = get_friend_id(borrower_name)

        # --- VALIDATION ---
        if borrower_id is None:
            return f"❌ Error: Friend '{borrower_name}' not found. Please add them first."
        if lender_id is None:
            return f"❌ Error: Friend '{lender_name}' not found. Please add them first."

        # --- SAVE TO DB ---
        supabase = get_client()
        today = date.today().strftime("%Y-%m-%d")

        data = {
            "date": today,
            "borrower_id": borrower_id,  # Using correct ID (e.g., 11 or 13)
            "lender_id": lender_id,  # Using correct ID
            "amount": amount,
            "description": description,
            "status": "Active"
        }

        supabase.table("debts").insert(data).execute()

        return f"✅ Success: {borrower_name} owes {lender_name} ₹{amount}"

    except Exception as e:
        return f"❌ Database Exception: {str(e)}"


def record_payment(payer_name, receiver_name, payment_amount):
    try:
        supabase = get_client()
        payer_id = get_friend_id(payer_name)
        receiver_id = get_friend_id(receiver_name)

        if payer_id is None or receiver_id is None:
            return "❌ Error: Friend not found."

        # Find active debts where the payer is the borrower
        res = supabase.table("debts").select("id, amount") \
            .eq("borrower_id", payer_id) \
            .eq("lender_id", receiver_id) \
            .eq("status", "Active") \
            .order("id").execute()

        active_debts = res.data
        if not active_debts:
            return f"⚠️ No active debts found for {payer_name} -> {receiver_name}."

        remaining = float(payment_amount)
        today = date.today().strftime("%Y-%m-%d")
        messages = []

        for debt in active_debts:
            if remaining <= 0: break

            # Check previously paid amount
            paid_res = supabase.table("payments").select("amount").eq("debt_id", debt['id']).execute()
            already_paid = sum(float(p['amount']) for p in paid_res.data)

            balance = float(debt['amount']) - already_paid
            pay_chunk = min(remaining, balance)

            if pay_chunk > 0:
                p_data = {
                    "date": today,
                    "debt_id": debt['id'],
                    "payer_id": payer_id,
                    "amount": pay_chunk
                }

                supabase.table("payments").insert(p_data).execute()

                if (already_paid + pay_chunk) >= float(debt['amount']):
                    supabase.table("debts").update({"status": "Settled"}).eq("id", debt['id']).execute()
                    messages.append(f"Settled Debt #{debt['id']}")

                remaining -= pay_chunk

        return f"✅ Payment recorded. {', '.join(messages)}"
    except Exception as e:
        return f"❌ Error logging payment: {str(e)}"