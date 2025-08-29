import streamlit as st
import json
import pandas as pd
from framework import nav_bar, sheet, authentication, update_history, log

if "log" not in st.session_state:
    st.session_state["log"] = log.MasterLogger()

nav_bar.NavBar().render()

st.title("Welcome to the Spendings Tracker App", anchor=None)

def total_balance(spendings_history, income_history) -> None:
    st.header("Total Balance")
    total_balance_cols = st.columns(3)
    if spendings_history:
        total_spendings = sum([i["Amount"] for i in spendings_history])
        total_balance_cols[0].metric("Total Spendings", f"${total_spendings:.2f}", f"${spendings_history[-1]['Amount']:.2f}", delta_color="inverse")
    else:
        total_balance_cols[0].metric("Total Spendings", "$0.00")
        total_balance_cols[0].write("No spendings history available.")
    if income_history:
        total_income = sum([i["Amount"] for i in income_history])
        total_balance_cols[1].metric("Total Income", f"${total_income:.2f}", f"${income_history[-1]['Amount']:.2f}", delta_color="normal")
        total_balance_cols[2].metric("Net Income", f"${total_income-total_spendings:.2f}", f"${income_history[-1]['Amount']-spendings_history[-1]['Amount']:.2f}", delta_color="normal")
    else:
        total_balance_cols[1].metric("Total Income", "$0.00")
        total_balance_cols[1].write("No income history available.")
        total_balance_cols[2].metric("Net Income", "$0.00")
        total_balance_cols[2].write("No net income history available.")

def transactions_data_editor(spendings_history:list[dict], income_history:list[dict]) -> None:
    """
        Edit transactions data.
        
        Args:
        - spendings_history (list): List of spendings data.
        - income_history (list): List of income data.
    """
    with open("settings/transaction_types.json", "r"):
        transaction_types = json.load(open("settings/transaction_types.json", "r"))            
    st.header("Transactions")
    history_tabs = st.tabs(["Spendings", "Income"])
    with history_tabs[0]:
        st.subheader("Spendings History")
        if spendings_history:
            edited_spenings = st.data_editor(spendings_history, use_container_width=True, column_config={
                "Number":st.column_config.Column(disabled=True),
                "Amount":st.column_config.NumberColumn(required=True, min_value=0, step=0.01),
                "Date":st.column_config.DateColumn(required=True),
                "Type":st.column_config.SelectboxColumn(
                width="small",
                options=transaction_types["spending_types"],
                required=True,),
                "Comments":st.column_config.TextColumn(),
            })
            update_spendings = st.button("Update Spendings", type="primary")
            if update_spendings:
                updated_spendings = update_history.update_history("spendings", st.session_state["sheet"], edited_spenings, spendings_history)
                if updated_spendings:
                    st.session_state["log"].log_info("[UPDATED] Spendings history updated.")
                    st.rerun(scope="app")
        else:
            st.warning("No spendings history available.")
    with history_tabs[1]:
        st.subheader("Income History")
        if income_history:
            edited_income = st.data_editor(income_history, use_container_width=True, column_config={
                "Number":st.column_config.Column(disabled=True),
                "Amount":st.column_config.NumberColumn(required=True, min_value=0, step=0.01),
                "Date":st.column_config.DateColumn(required=True),
                "Type":st.column_config.SelectboxColumn(
                width="small",
                options=transaction_types["income_types"],
                required=True),
                "Comments":st.column_config.TextColumn()
            })
            update_income = st.button("Update Income", type="primary")
            if update_income:
                updated_income = update_history.update_history("income", st.session_state["sheet"], edited_income, income_history)
                if updated_income:
                    st.session_state["log"].log_info("[UPDATED] Income history updated.")
                    st.rerun(scope="app")
        else:
            st.warning("No income history available.")


def net_spending_area_chart(spendings_history, income_history):
    """
    Display an area chart for net spending over time.

    Args:
        spendings_history (list): List of spendings data.
        income_history (list): List of income data.
    """
    if spendings_history and income_history:
        spendings_df = pd.DataFrame(spendings_history, columns=["Amount", "Date", "Type", "Comments"])
        income_df = pd.DataFrame(income_history, columns=["Amount", "Date", "Type", "Comments"])

        spendings_df["Amount"] = spendings_df["Amount"].astype(float)
        income_df["Amount"] = income_df["Amount"].astype(float)

        spendings_by_date = spendings_df.groupby("Date")["Amount"].sum()
        income_by_date = income_df.groupby("Date")["Amount"].sum()

        net_spending_by_date = spendings_by_date.subtract(income_by_date, fill_value=0).reset_index()
        net_spending_by_date.columns = ["Date", "Net Spending"]

        st.subheader("Net Spending Over Time")
        st.area_chart(net_spending_by_date.set_index("Date"))


def display_spending_by_category(spendings_history):
    """
    Display a bar chart of spending amounts by category.

    Args:
        spendings_history (list): List of spendings data.
    """
    if spendings_history:
        amount = {j:0 for j in list(set([i["Type"] for i in spendings_history]))}
        for i in spendings_history:
            amount[i["Type"]]+=(i["Amount"])
        spendings_df = pd.DataFrame(
            {
                "Type": amount.keys(),
                "Amount $USD": amount.values()
            }
        )
        st.subheader("Income by Category")
        st.bar_chart(spendings_df, x="Type", y="Amount $USD")


def display_income_by_category(income_history):
    """
    Display a bar chart of income amounts by category.

    Args:
        income_history (list): List of income data.
    """
    if income_history:
        amount = {j:0 for j in list(set([i["Type"] for i in income_history]))}
        for i in income_history:
            amount[i["Type"]]+=(i["Amount"])
        income_df = pd.DataFrame(
            {
                "Type": amount.keys(),
                "Amount $USD": amount.values()
            }
        )
        st.subheader("Income by Category")
        st.bar_chart(income_df, x="Type", y="Amount $USD")



if ("authenticated" not in st.session_state) or not st.session_state["authenticated"]:
    authenticated = authentication.authenticate_user()
    st.warning("Authentication required to access the application.")
    if authenticated:
        st.session_state["log"].log_info("[LOG IN] User logged in.")
        st.rerun(scope="app")
else:
    if "sheet" not in st.session_state:
        st.session_state["sheet"] = sheet.SheetLogger()
        st.session_state["log"].log_info("[DATA RETREIVED] Data retreived from Google Sheets.")
    if "log" not in st.session_state:
        st.session_state["log"] = log.MasterLogger()

    income_history = st.session_state["sheet"].fetch_income(True)
    spendings_history = st.session_state["sheet"].fetch_spendings(True)
    total_balance(spendings_history, income_history)
    transactions_data_editor(spendings_history, income_history)
    net_spending_area_chart(spendings_history, income_history)
    display_spending_by_category(spendings_history)
    display_income_by_category(income_history)


