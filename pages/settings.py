import streamlit as st
import json
from framework import nav_bar

if ("authenticated" not in st.session_state) or not st.session_state["authenticated"]:
    st.switch_page("main.py")
elif ("sheet" not in st.session_state):
    st.switch_page("main.py")
elif ("log" not in st.session_state):
    st.switch_page("main.py")

your_information = dict(st.secrets.login)
db_info = dict(st.secrets.db_info)


nav_bar.NavBar().render()
st.title("Settings")

@st.fragment
def transaction_types_editor() -> None:
    st.header("Edit Transaction Types")
    with open("settings/transaction_types.json", "r") as file:
        transaction_types = json.load(file)
    transaction_types_tabs = st.tabs(["Spendings", "Income"])
    with transaction_types_tabs[0]:
        st.subheader("Spendings Transaction Types")
        edited_spending_types = st.data_editor(transaction_types["spending_types"], use_container_width=True, num_rows="dynamic")
        if st.button("Save", key="ssts") and edited_spending_types != transaction_types["spending_types"]:
            edited_spending_types = [i for i in edited_spending_types if i != ""]
            transaction_types["spending_types"] = edited_spending_types
            json.dump(transaction_types, open("settings/transaction_types.json", "w"), indent=4)
            st.session_state["log"].log_info("[UPDATED] Spendings transaction types updated.")
    with transaction_types_tabs[1]:
        st.subheader("Income Transaction Types")
        edited_income_types = st.data_editor(transaction_types["income_types"], use_container_width=True, num_rows="dynamic")
        if st.button("Save", key="ssti") and edited_income_types != transaction_types["income_types"]:
            edited_income_types = [i for i in edited_income_types if i != ""]
            transaction_types["income_types"] = edited_income_types
            json.dump(transaction_types, open("settings/transaction_types.json", "w"), indent=4)
            st.session_state["log"].log_info("[UPDATED] Income transaction types updated.")


@st.dialog("Change Password")
def change_password() -> bool:
    st.header("Change Password")
    current = st.text_input("Current Password", type="password")
    new_1 = st.text_input("New Password", type="password")
    new_2 = st.text_input("Confirm New Password", type="password")
    if st.button("Change"):
        if (current==your_information["password"]) and (new_1==new_2):
            st.session_state["log"].log_info("[UPDATED] Password updated.")
            st.success("Password change would be saved here if secrets.toml was writable.")
            return True


def your_infomation() -> None:
    st.header("Your Information")
    st.write(f"Your email is: {your_information['email']}")
    if st.button("Change Password"):
        if change_password():
            st.session_state["authenticated"] = False
            st.rerun(scope="app")

def data_base_info() -> None:
    st.header("Database Information")
    st.write(f"Your current database app is: {db_info['type']}")
    st.write(f"Your current database url is: {db_info['url']}")

@st.dialog("Clear Logs")
def clear_logs() -> None:
    st.write("Are you sure you want to clear the logs?")
    if st.text_input("Type the message: \"I want to clear the logs.\"") == "I want to clear the logs.":
        if st.button("Clear"):
            st.session_state["log"].clear_log()
            st.session_state["log"].log_info("[LOGS CLEARED] Logs cleared.")
            st.success("Logs cleared")
            st.switch_page("main.py")

def logs() -> None:
    st.header("Logs")
    logs = st.session_state["log"].fetch_logs()
    st.json(logs, expanded=True)
    if st.button("Clear Logs", type="primary"):
        clear_logs()

@st.dialog("Clear Transactions")
def clear_transactions_dialog(type:str) -> None:
    """
    Clear transactions dialog.
    
    Args:
        type (str): Type of transactions to clear. 'spendings' or 'income'.
    """
    st.write("Are you sure you want to clear the transactions?")
    if st.text_input(f"Type the message: \"I want to clear my {type} history.\"") == f"I want to clear my {type} history.":
        if st.button("Clear"):
            if type == "spendings":
                st.session_state["sheet"].clear_spending_sheet()
                st.session_state["log"].log_info("[TRANSACTIONS CLEARED] Spendings transactions history removed.")
                st.success("Spendings transactions history removed")
                st.switch_page("main.py")
            elif type == "income":
                st.session_state["sheet"].clear_income_sheet()
                st.session_state["log"].log_info("[TRANSACTIONS CLEARED] Income transactions history removed.")
                st.success("Income transactions history removed")
                st.switch_page("main.py")

def clear_transactions() -> None:
    st.header("Clear Transactions History")
    clear_transactions_cols = st.columns([1, 1])
    if clear_transactions_cols[0].button("Clear Spendings History", use_container_width=True, type="primary"):
        clear_transactions_dialog("spendings")
    if clear_transactions_cols[1].button("Clear Income History", use_container_width=True, type="primary"):
        clear_transactions_dialog("income")

@st.dialog("Log Out")
def log_out() -> None:
    st.write("Are you sure you want to log out?")
    if st.button("Yes", use_container_width=True, type="primary"):
        st.session_state["authenticated"] = False
        st.success("Logging Out")
        st.session_state["log"].log_info("[LOG OUT] User logged out.")
        st.rerun(scope="app")


your_infomation()
data_base_info()
transaction_types_editor()
logs()
clear_transactions()
st.divider()
if st.button("Log Out", type="secondary"):
    log_out()
