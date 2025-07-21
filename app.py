# app.py (Reverted to end of Phase 3)
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px # Still using Plotly for nice charts

# Import only necessary functions from database.py for basic functionality
from database import (
    create_tables,
    add_transaction,
    get_all_transactions
)

# --- Initial Setup ---
# Ensure database tables are created every time the app starts
create_tables()

# Configure the Streamlit page settings
st.set_page_config(
    layout="wide",
    page_title="Personal Finance Dashboard (Basic)",
    page_icon="💰"
)

# --- Header Section ---
st.title("💰 Personal Finance Dashboard")
st.markdown("""
    Track your income and expenses and view basic financial reports.
    Use the sidebar to navigate between sections.
""")
st.markdown("---")

# --- Sidebar for Navigation ---
st.sidebar.title("Navigation")
# Only basic pages in the sidebar
page = st.sidebar.radio("Go to", [
    "Add Transaction",
    "View Transactions",
    "Reports"
])
st.sidebar.markdown("---")
st.sidebar.info("Developed by Harshit Pahuja. Feel free to connect on LinkedIn!")


# --- Page Content based on Navigation ---

# --- Add Transaction Page ---
if page == "Add Transaction":
    st.header("➕ Add New Transaction")
    st.markdown("Use the form below to record your financial activities.")

    with st.form("transaction_form", clear_on_submit=True):
        current_gurugram_date = datetime.date(2025, 7, 21) # Current date
        date = st.date_input("Date", current_gurugram_date)

        description = st.text_input("Description", placeholder="e.g., Coffee, Salary")
        amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
        
        type = st.radio("Type", ["Expense", "Income"])
        
        # Hardcoded categories (as there's no category management feature in this version)
        if type == "Expense":
            categories = ["Food", "Transport", "Utilities", "Rent", "Entertainment", "Shopping", "Health", "Education", "Other Expense"]
        else: # Income
            categories = ["Salary", "Freelance", "Investment", "Gift", "Other Income"]
        
        category = st.selectbox("Category", categories)

        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            if not description.strip():
                st.error("Please enter a description.")
            elif amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                try:
                    add_transaction(str(date), description.strip(), float(amount), category, type.lower())
                    st.success("Transaction added successfully! 🎉")
                    st.balloons()
                except Exception as e:
                    st.error(f"An error occurred while adding transaction: {e}")
                    st.exception(e)


# --- View Transactions Page ---
elif page == "View Transactions":
    st.header("📋 All Transactions")
    st.markdown("Review and filter your recorded financial activities.")

    transactions_df = get_all_transactions()

    if transactions_df.empty:
        st.info("No transactions recorded yet. Add some in the 'Add Transaction' section!")
    else:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])

        # --- Filtering Options ---
        st.subheader("Filter Transactions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unique_types = transactions_df['type'].unique().tolist()
            selected_type = st.selectbox("By Type", ["All"] + unique_types)
        
        with col2:
            unique_categories = transactions_df['category'].unique().tolist()
            selected_category = st.selectbox("By Category", ["All"] + unique_categories)

        with col3:
            min_date = transactions_df['date'].min().date()
            max_date = transactions_df['date'].max().date()
            date_range = st.date_input("By Date Range", value=(min_date, max_date))

        filtered_df = transactions_df.copy()
        if selected_type != "All":
            filtered_df = filtered_df[filtered_df['type'] == selected_type]
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date <= end_date)]
        elif len(date_range) == 1:
            start_date = date_range[0]
            filtered_df = filtered_df[filtered_df['date'].dt.date == start_date]

        st.dataframe(filtered_df, use_container_width=True)

        st.markdown("---")

        # --- Current Balance Calculation ---
        total_income = filtered_df[filtered_df['type'] == 'income']['amount'].sum()
        total_expense = filtered_df[filtered_df['type'] == 'expense']['amount'].sum()
        current_balance = total_income - total_expense

        st.subheader("Current Financial Summary (Filtered View)")
        col_i, col_e, col_b = st.columns(3)
        with col_i:
            st.metric(label="Total Income", value=f"₹{total_income:,.2f}", delta_color="normal")
        with col_e:
            st.metric(label="Total Expense", value=f"₹{total_expense:,.2f}", delta_color="inverse")
        with col_b:
            st.metric(label="Net Balance", value=f"₹{current_balance:,.2f}")
        
        st.markdown("---")


# --- Reports Page ---
elif page == "Reports":
    st.header("📊 Financial Reports & Insights")
    st.markdown("Explore your spending patterns and financial trends visually.")

    transactions_df = get_all_transactions()

    if transactions_df.empty:
        st.info("No transactions recorded yet to generate reports. Add some in the 'Add Transaction' section!")
        st.stop()

    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    st.subheader("Report Filters")
    all_years = sorted(transactions_df['date'].dt.year.unique().tolist(), reverse=True)
    selected_year = st.selectbox("Select Year", ["All Years"] + all_years)

    report_df = transactions_df.copy()
    if selected_year != "All Years":
        report_df = report_df[report_df['date'].dt.year == selected_year]
    
    if report_df.empty:
        st.warning(f"No transactions found for {selected_year}. Please choose another year or add more data.")
        st.stop()


    # --- 1. Expenses by Category (Pie Chart) ---
    st.subheader("1. Expense Breakdown by Category")
    expense_df = report_df[report_df['type'] == 'expense']

    if not expense_df.empty:
        category_spending = expense_df.groupby('category')['amount'].sum