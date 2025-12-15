from mcp.server.fastmcp import FastMCP
from modules import finance_manager, social_manager, report_generator

# Initialize the MCP Server
# You can give it a custom name like "FiscalFit"
mcp = FastMCP("Finance-Tracker")


# --- TOOL 1: Log Personal Expense ---
@mcp.tool()
def log_personal_expense(item: str, amount: float, category: str = "Food", is_healthy: bool = None) -> str:
    """
    Logs a personal expense.
    IMPORTANT: If you don't know if the item is healthy, pass is_healthy=None.
    The system will check the database and tell you if it needs clarification.
    """
    # Call the logic we built in finance_manager
    result = finance_manager.log_expense(item, amount, category, is_healthy)

    # Handle the interactive "Unknown Health" case
    if result.get("status") == "NEEDS_CLARIFICATION":
        return (
            f"STOP: I cannot log '{item}' yet because I don't know if it is healthy. "
            f"Please ask the user: 'Is {item} considered healthy or unhealthy?' "
            f"Once they answer, use the 'learn_food_health' tool."
        )

    # Success case
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
    Example: lender='Me', borrower='Pratham', amount=90
    """
    result = social_manager.log_debt(borrower, lender, amount, description)
    # Ensure we return a string, even if the module returned a dict
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


# --- TOOL 6: Generate Report (Excel + Summary) ---
@mcp.tool()
def generate_monthly_report(month: int = None, year: int = None) -> str:
    """
    Generates a text summary AND creates an Excel file (reports/data.xlsx).
    Returns the summary text to be displayed to the user.
    """
    # This calls the function we updated in the previous step
    # It returns a ready-to-print string containing the Excel path and stats
    return report_generator.generate_monthly_report(month, year)


if __name__ == "__main__":
    # This keeps the server running so Claude can connect to it
    mcp.run()