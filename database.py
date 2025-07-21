# database.py (Reverted to only transactions table)
import sqlite3
import pandas as pd # Used for easily reading SQL data into a DataFrame

# Define the database file name
DB_FILE = 'finance_tracker.db'

def create_tables():
    """
    Connects to the SQLite database and creates ONLY the 'transactions' table
    if it doesn't already exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create transactions table (only this table in this version)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense'))
        )
    ''')

    conn.commit()
    conn.close()

    # No default categories added here, as category management is removed.


def add_transaction(date, description, amount, category, type):
    """Adds a new transaction record."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (date, description, amount, category, type)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, description, amount, category, type))
    conn.commit()
    conn.close()

def get_all_transactions():
    """Retrieves all transactions as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
    conn.close()
    return df

# Removed delete_transaction, update_transaction, and all category/budget functions.


# This block allows you to run database.py directly to set up the database
# and optionally add some test data, without needing to run the full Streamlit app.
if __name__ == '__main__':
    create_tables()
    print(f"Database '{DB_FILE}' and 'transactions' table ensured.")
    # You can uncomment these lines for initial testing to add some dummy data
    # print("\nAdding some test transactions...")
    # add_transaction('2025-07-20', 'Initial Salary', 50000.0, 'Income', 'income')
    # add_transaction('2025-07-21', 'Morning Coffee', 150.0, 'Food', 'expense')
    # add_transaction('2025-07-21', 'Bus Fare', 50.0, 'Transport', 'expense')
    # add_transaction('2025-07-19', 'Groceries', 800.0, 'Food', 'expense')
    # add_transaction('2025-06-15', 'Freelance Project', 15000.0, 'Freelance', 'income')
    # add_transaction('2025-06-20', 'Electricity Bill', 1200.0, 'Utilities', 'expense')
    # add_transaction('2025-07-10', 'Dinner with Friends', 750.0, 'Entertainment', 'expense')
    # print("Test transactions added.")

    # print("\nFetching all transactions after adding test data:")
    # print(get_all_transactions())