import argparse
from modules import finance_manager, social_manager, report_generator, ocr_handler

# Note: We removed 'initialize_db' because Supabase tables are already created online.

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="FiscalFit Cloud CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- COMMAND: log_expense ---
    # Usage: python main.py log_expense "Burger" 15.50 --cat Food
    parser_exp = subparsers.add_parser("log_expense", help="Log a personal expense")
    parser_exp.add_argument("item", type=str, help="Name of the item")
    parser_exp.add_argument("amount", type=float, help="Cost of the item")
    parser_exp.add_argument("--cat", type=str, default="General", help="Category (e.g., Food)")
    parser_exp.add_argument("--healthy", type=int, choices=[0, 1], help="1 for Healthy, 0 for Unhealthy (Optional)")

    # --- COMMAND: add_friend ---
    parser_friend = subparsers.add_parser("add_friend", help="Register a new friend")
    parser_friend.add_argument("name", type=str, help="Friend's name")
    parser_friend.add_argument("--phone", type=str, help="Phone number (Optional)")

    # --- COMMAND: log_debt ---
    parser_debt = subparsers.add_parser("log_debt", help="Log a debt (Borrower owes Lender)")
    parser_debt.add_argument("borrower", type=str, help="Who owes money")
    parser_debt.add_argument("lender", type=str, help="Who lent money")
    parser_debt.add_argument("amount", type=float, help="Amount owed")
    parser_debt.add_argument("--desc", type=str, default="Loan", help="Description")

    # --- COMMAND: record_payment ---
    parser_pay = subparsers.add_parser("record_payment", help="Record a payback")
    parser_pay.add_argument("payer", type=str, help="Who is paying")
    parser_pay.add_argument("receiver", type=str, help="Who is receiving")
    parser_pay.add_argument("amount", type=float, help="Amount paid")

    # --- COMMAND: report ---
    parser_rep = subparsers.add_parser("report", help="Generate monthly graphs & data")
    parser_rep.add_argument("--month", type=int, help="Month number (1-12)")
    parser_rep.add_argument("--year", type=int, help="Year (e.g., 2023)")

    # --- COMMAND: list_friends ---
    subparsers.add_parser("list_friends", help="Show all registered friends")

    # --- COMMAND: scan_receipt ---
    parser_scan = subparsers.add_parser("scan_receipt", help="OCR a receipt image")
    parser_scan.add_argument("path", type=str, help="Path to image file")

    # Parse arguments
    args = parser.parse_args()

    # Route to the correct function
    if args.command == "log_expense":
        # Convert integer 1/0 to Boolean if provided
        is_healthy = bool(args.healthy) if args.healthy is not None else None

        # 1. Try to log the expense to Cloud
        result = finance_manager.log_expense(args.item, args.amount, args.cat, is_healthy)

        # 2. Check if we need clarification (The Interactive Update)
        if result.get("status") == "NEEDS_CLARIFICATION":
            print(f"\n❓ Unknown Item: '{args.item}'")
            print("   Is this Healthy (1) or Unhealthy (0)?")

            while True:
                user_choice = input("   Enter 1 or 0: ").strip()
                if user_choice in ['1', '0']:
                    # Learn the new item (Locally or Cloud)
                    is_healthy_bool = (user_choice == '1')
                    finance_manager.learn_item_health(args.item, is_healthy_bool)

                    # Retry logging
                    print("   Saving to Cloud...")
                    result = finance_manager.log_expense(args.item, args.amount, args.cat, is_healthy_bool)
                    break
                else:
                    print("   Invalid input. Please enter 1 for Healthy or 0 for Unhealthy.")

        # 3. Print Final Result
        if result.get("status") == "SUCCESS":
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result.get('message', 'Unknown Error')}")

    elif args.command == "add_friend":
        # Now returns a string, so we print it
        print(social_manager.add_friend(args.name, args.phone))

    elif args.command == "log_debt":
        res = social_manager.log_debt(args.borrower, args.lender, args.amount, args.desc)
        print(res)

    elif args.command == "record_payment":
        res = social_manager.record_payment(args.payer, args.receiver, args.amount)
        print(res)

    elif args.command == "report":
        # Now returns the summary text, so we print it
        print(report_generator.generate_monthly_report(args.month, args.year))

    elif args.command == "list_friends":
        friends = social_manager.list_friends()
        print("--- Friends List (Cloud) ---")
        for f in friends:
            print(f"- {f}")

    elif args.command == "scan_receipt":
        ocr_handler.scan_receipt(args.path)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()