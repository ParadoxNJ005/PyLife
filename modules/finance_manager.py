from datetime import date
from modules.database import get_client


# --- CORE FUNCTIONS (Cloud Version) ---

def check_item_health(item):
    """Checks Cloud DB for item health status."""
    supabase = get_client()
    try:
        # Search for the item (case-insensitive)
        # .ilike ensures we find "Burger" even if you search "burger"
        response = supabase.table("item_health").select("is_healthy").ilike("item", item.strip()).execute()
        if response.data:
            return response.data[0]['is_healthy']
    except Exception:
        pass
    return None


def learn_item_health(item, is_healthy):
    """Saves item health status to Cloud DB."""
    supabase = get_client()
    try:
        clean_item = item.lower().strip()
        data = {"item": clean_item, "is_healthy": is_healthy}

        # 'upsert' means: Insert if new, Update if exists
        supabase.table("item_health").upsert(data, on_conflict="item").execute()
        print(f"🧠 Cloud Brain: Learned that '{clean_item}' is {'Healthy' if is_healthy else 'Unhealthy'}")
    except Exception as e:
        print(f"Error learning item: {e}")


def log_expense(item, amount, category="Food", is_healthy=None):
    """Logs a personal expense to Supabase."""

    # 1. Strict Health Check
    if is_healthy is None:
        known_status = check_item_health(item)
        if known_status is not None:
            is_healthy = known_status
        else:
            # If we don't know, stop and ask the user
            return {
                "status": "NEEDS_CLARIFICATION",
                "item": item,
                "amount": amount
            }

    # 2. Supabase Insert
    supabase = get_client()
    today = date.today().strftime("%Y-%m-%d")

    data = {
        "date": today,
        "item": item,
        "amount": amount,
        "category": category,
        "is_healthy": is_healthy
    }

    try:
        # .insert() sends data to the cloud 'expenses' table
        supabase.table("expenses").insert(data).execute()

        health_str = "Healthy" if is_healthy else "Unhealthy"
        return {"status": "SUCCESS", "message": f"☁️ Logged to Cloud: {item} (₹{amount}) as {health_str}"}

    except Exception as e:
        return {"status": "ERROR", "message": f"Supabase Error: {str(e)}"}