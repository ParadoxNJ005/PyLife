from mcp.server.fastmcp import FastMCP
from modules import finance_manager, social_manager
from modules.database import get_client

# Initialize the MCP Server
mcp = FastMCP("Finance-Tracker")


# ==============================================================================
# 📝 SECTION 1: DATA ENTRY TOOLS (WRITE)
# ==============================================================================

# --- TOOL 1: Log Personal Expense ---
@mcp.tool()
def log_personal_expense(item: str, amount: float, category: str = "Food", is_healthy: bool = None) -> str:
    """
    Logs a personal expense.
    IMPORTANT: If you don't know if the item is healthy, pass is_healthy=None.
    The system will check the database and tell you if it needs clarification.
    """
    result = finance_manager.log_expense(item, amount, category, is_healthy)

    if result.get("status") == "NEEDS_CLARIFICATION":
        return (
            f"STOP: I cannot log '{item}' yet because I don't know if it is healthy. "
            f"Please ask the user: 'Is {item} considered healthy or unhealthy?' "
            f"Once they answer, use the 'learn_food_health' tool."
        )

    return result["message"]


# --- TOOL 2: Learn Health Status ---
@mcp.tool()
def learn_food_health(item: str, is_healthy: bool) -> str:
    """
    Teaches the system if a specific food item is healthy (True) or unhealthy (False).
    Use this when the user answers your clarification question.
    """
    finance_manager.learn_item_health(item, is_healthy)
    status_str = "Healthy" if is_healthy else "Unhealthy"
    return f"Success: I have learned that '{item}' is {status_str}. You can now try logging the expense again."


# --- TOOL 3: Add Friend ---
@mcp.tool()
def add_friend(name: str, phone: str = None) -> str:
    """Registers a new friend for tracking shared expenses/debts."""
    return social_manager.add_friend(name, phone)


# --- TOOL 4: Log Debt ---
@mcp.tool()
def log_debt(borrower: str, lender: str, amount: float, description: str = "Loan") -> str:
    """
    Logs that one person owes another money.
    - If user owes someone: borrower='Me', lender='Name'
    - If someone owes user: borrower='Name', lender='Me'
    """
    result = social_manager.log_debt(borrower, lender, amount, description)
    if isinstance(result, dict):
        return result.get("message", str(result))
    return str(result)


# --- TOOL 5: Record Payment ---
@mcp.tool()
def record_payment(payer: str, receiver: str, amount: float) -> str:
    """Records a payment (payback) and automatically settles the oldest debts."""
    result = social_manager.record_payment(payer, receiver, amount)
    if isinstance(result, dict):
        return result.get("message", str(result))
    return str(result)


# ==============================================================================
# 🧠 SECTION 2: SMART ANALYST TOOLS (READ / VIEW)
# ==============================================================================

# --- TOOL 6: Social Finance Manager (Unified) ---
@mcp.tool()
def check_social_finances(query_type: str, person: str = None) -> str:
    """
    The Master Tool for social finances. Can answer history OR balance questions.

    Args:
        query_type: 'BALANCE' for questions like "Who owes me?", "How much does X owe?".
                    'HISTORY' for questions like "History with X", "What payments did X make?".
        person: (Optional) Name of specific person to filter by.
    """
    supabase = get_client()

    # RPC call to Supabase
    try:
        response = supabase.rpc("query_social_ledger", {
            "target_person": person,
            "query_mode": query_type.upper()
        }).execute()

        data = response.data
        if not data:
            return f"No records found for '{person or 'everyone'}' in mode {query_type}."

        # Format Output
        lines = [f"--- Social Report ({query_type}) ---"]
        for row in data:
            amt = f"₹{row['amount']}"
            if query_type.upper() == "BALANCE":
                lines.append(f"💰 {row['person']} owes: {amt}")
            else:
                lines.append(f"{row['date']} | {row['person']} | {row['description']} | {amt}")

        return "\n".join(lines)

    except Exception as e:
        return f"Database Error: {str(e)}"


# --- TOOL 7: Expense Analytics ---
@mcp.tool()
def analyze_spending(month: str = None) -> str:
    """
    Analyzes personal spending by Category and Health.

    Args:
        month: Format 'YYYY-MM' (e.g. '2023-11'). Defaults to current month if omitted.
    """
    supabase = get_client()

    try:
        # RPC call
        response = supabase.rpc("get_expense_stats", {"target_month": month}).execute()
        data = response.data

        if not data:
            return f"No spending data found for {month}."

        lines = [f"--- Spending Analysis ({month or 'Current Month'}) ---"]
        for row in data:
            lines.append(f"• {row['category']} ({row['health_status']}): ₹{row['total_spent']}")

        return "\n".join(lines)

    except Exception as e:
        return f"Database Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()