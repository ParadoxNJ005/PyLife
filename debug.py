from datetime import date
from modules.database import get_client


def inject_payment_data():
    supabase = get_client()
    print("\n--- 💉 INJECTING TEST PAYMENT DATA ---")

    try:
        # 1. FIND AN ACTIVE DEBT
        # We need a valid debt_id to link the payment to.
        print("1. Searching for an active debt to pay off...")
        debt_res = supabase.table("debts").select("*").eq("status", "Active").limit(1).execute()

        debt_id = None
        payer_id = None
        amount_to_pay = 50

        if debt_res.data:
            # Use existing debt
            debt = debt_res.data[0]
            debt_id = debt['id']
            payer_id = debt['borrower_id']  # The borrower pays back
            print(f"   ✅ Found Active Debt #{debt_id}: Borrower {payer_id} owes Lender {debt['lender_id']}")
        else:
            # Create a dummy debt if none exists
            print("   ⚠️ No active debts found. Creating a dummy debt first...")
            dummy_debt = {
                "date": date.today().strftime("%Y-%m-%d"),
                "borrower_id": 0,  # "Me"
                "lender_id": 0,  # "Me" (Self-loan for testing) - or use a real friend ID if known
                "amount": 100,
                "description": "Auto-Generated Test Debt",
                "status": "Active"
            }
            # We must use a valid friend ID if constraints are on, but since we disabled them, 0 is fine.
            debt_insert = supabase.table("debts").insert(dummy_debt).execute()

            # Re-fetch the debt to get the ID (since .select() is broken on insert for you)
            debt_res = supabase.table("debts").select("id").order("id", desc=True).limit(1).execute()
            debt_id = debt_res.data[0]['id']
            payer_id = 0
            print(f"   ✅ Created Dummy Debt #{debt_id}")

        # 2. INSERT THE PAYMENT
        print(f"\n2. Inserting Payment of ₹{amount_to_pay} for Debt #{debt_id}...")

        payment_data = {
            "date": date.today().strftime("%Y-%m-%d"),
            "debt_id": debt_id,
            "payer_id": payer_id,
            "amount": amount_to_pay
        }

        # The Fix: Standard insert without .select()
        supabase.table("payments").insert(payment_data).execute()
        print("   ✅ SUCCESS: Payment data sent to Supabase.")

        # 3. VERIFY
        print("\n3. Verifying entry...")
        check = supabase.table("payments").select("*").order("id", desc=True).limit(1).execute()
        if check.data:
            latest = check.data[0]
            print(f"   🎉 Confirmed! Latest Payment ID: {latest['id']} | Amount: ₹{latest['amount']}")
        else:
            print("   ❌ Verification failed. Table is still empty.")

    except Exception as e:
        print(f"❌ Error injecting data: {e}")


if __name__ == "__main__":
    inject_payment_data()