from mcp.server.fastmcp import FastMCP
from modules import finance_manager, social_manager, report_generator

mcp = FastMCP("Finance-Tracker")


@mcp.tool()
def log_expense(item: str, amount: float, category: str = "General", is_healthy: bool = None) -> str:
    """Logs a personal expense. Set is_healthy to True (1) or False (0) if known."""
    # We call your existing function directly
    result = finance_manager.log_expense(item, amount, category, is_healthy)
    return str(result)


@mcp.tool()
def add_friend(name: str, phone: str = None) -> str:
    """Registers a new friend for splitwise tracking."""
    return social_manager.add_friend(name, phone)


@mcp.tool()
def log_debt(borrower: str, lender: str, amount: float, description: str = "Loan") -> str:
    """Logs that one person owes another money."""
    return social_manager.log_debt(borrower, lender, amount, description)


@mcp.tool()
def record_payment(payer: str, receiver: str, amount: float) -> str:
    """Records a payment and automatically settles oldest debts."""
    return social_manager.record_payment(payer, receiver, amount)


@mcp.tool()
def generate_monthly_report(month: int = None, year: int = None) -> str:
    """Generates graphs and data tables for a specific month."""
    data = report_generator.generate_monthly_report(month, year)
    if data == "No Data":
        return "No data found for this month."

    return f"Report Generated. Total Spent: ${data['total_spent']}. Graphs saved at: {data['graphs']}"


if __name__ == "__main__":
    mcp.run()