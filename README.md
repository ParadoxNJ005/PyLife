# FiscalFit Cloud 🏋️‍♂️💸

**The AI Agent that tracks your Wallet and your Waistline.**

FiscalFit is a robust **MCP (Model Context Protocol) Server** that turns **Claude Desktop** into an intelligent personal finance and diet assistant. It allows you to log expenses, track debts with friends, and monitor your eating habits using simple natural language.

Unlike standard trackers, FiscalFit features a **"Human-in-the-Loop" learning system**—if it doesn't know if a food item is healthy, it asks you, learns the answer, and remembers it forever.

---

## 🚀 Key Features

### 🧠 1. Smart Expense & Diet Logging
* **Natural Language Entry:** Just say *"I bought a Salad for $12"* or *"Uber to work for $25"*.
* **Active Learning Loop:** If you log an unknown item (e.g., *"Galactic Cookie"*), the AI pauses to ask: *"Is this healthy?"*. Once you answer, it updates its database and never asks again.
* **Automatic Categorization:** Intelligent handling of categories (Food, Transport, Bills).

### 🤝 2. Social Finance Manager (Unified Ledger)
* **Track Debts:** *"I lent Pratham ₹500"* or *"I borrowed ₹200 from Rahul"*.
* **Unified History:** Combines loans and payments into a single chronological timeline.
* **Smart Settlements:** *"Rahul paid me back"* automatically settles the oldest debts first.
* **Complex Queries:** Ask *"Who owes me money?"* or *"What is my history with Pratham?"*.

### 🛡️ 3. Safe & Scalable Architecture
* **No Raw SQL:** The AI interacts with the database via **Secure RPC Functions**, preventing accidental data loss or hallucinations.
* **Database Views:** Heavy calculations (running balances, health stats) are handled by PostgreSQL Views, ensuring 100% mathematical accuracy.

---

## 🛠️ Architecture

* **Frontend:** Claude Desktop (AI Interface)
* **Backend:** Python (FastMCP)
* **Database:** Supabase (PostgreSQL)
* **Protocol:** Model Context Protocol (MCP)

---

## 📦 Installation & Setup

### 1. Prerequisites
* Python 3.10+
* [Claude Desktop App](https://claude.ai/download)
* A free [Supabase](https://supabase.com) account

### 2. Clone the Repository
```bash
git clone [https://github.com/yourusername/fiscalfit-cloud.git](https://github.com/yourusername/fiscalfit-cloud.git)
cd fiscalfit-cloud
3. Install Dependencies
It is recommended to use a virtual environment.

Bash

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

pip install mcp supabase python-dotenv
4. Configure Environment
Create a .env file in the root directory:

Ini, TOML

SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
5. Connect to Claude Desktop
Create or edit your Claude Desktop config file:

Mac: ~/Library/Application Support/Claude/claude_desktop_config.json

Windows: %APPDATA%\Claude\claude_desktop_config.json

Add this configuration (update the path!):

JSON

{
  "mcpServers": {
    "FiscalFit": {
      "command": "python",
      "args": ["C:\\Path\\To\\Your\\Project\\server.py"]
    }
  }
}
Note: Ensure your database schema is already deployed to Supabase.

🗣️ Usage Guide
Once connected, you can talk to Claude normally.

🥗 Tracking Expenses
"I bought a Burger for $15." "Log an Uber ride for $40." "I had a salad for lunch, cost 12."

🧠 The Learning Loop
User: "I bought a Matcha Latte for 8." Claude: "STOP: I don't know if 'Matcha Latte' is healthy. Is it?" User: "Yes, it is healthy." Claude: "Success. I have learned that. Expense logged."

💰 Managing Debts
"I lent Pratham 500 for dinner." "Rahul paid me back 200." "Who owes me money right now?" "What is my payment history with Pratham?"

📊 Analysis
"How much did I spend on healthy food this month?" "Did I spend more on junk food in January 2024?"

📄 License
This project is open-source. Feel free to use it to get your finances (and diet) in shape!
