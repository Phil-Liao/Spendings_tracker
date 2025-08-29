import streamlit as st
from framework import nav_bar, process_form
import json

if ("authenticated" not in st.session_state) or not st.session_state["authenticated"]:
    st.switch_page("main.py")
elif ("sheet" not in st.session_state):
    st.switch_page("main.py")
elif ("log" not in st.session_state):
    st.switch_page("main.py")

nav_bar.NavBar().render()

st.title("Income Page")

with open("settings/currencies.json", "r") as file:
    currencies = json.load(file)
with open("settings/transaction_types.json", "r") as file:
    income_types = json.load(file)

@st.dialog("Submitting")
def submitting(data:list[str, float, str, str, str, str]) -> bool:
    """
        data:
        type=spendings, income
        amount
        currency=three letter code
        date=DD/MM/YYYY
        type
        comment
    """
    st.spinner("Submitting...")
    submitted = process_form.process_form(data, st.session_state["sheet"])
    if submitted:
        st.session_state["log"].log_info("[SUBMITTED] Submitted the income form.")
        st.success("Submitted!")
    else:
        st.error("Something went wrong")

# Add a form to input the amount of income
with st.form("income_form", clear_on_submit=True):
    income_amount_cols = st.columns([8, 2])  # Create two columns: one for the amount and one for the currency
    with income_amount_cols[0]:
        income_amount = st.number_input("Enter the amount of income:", min_value=0.0, step=0.01)
    with income_amount_cols[1]:
        currency = st.selectbox("Currency", currencies["currencies"])

    transaction_date = st.date_input("Transaction Date", value=None, format="DD/MM/YYYY")

    transaction_type = st.selectbox("Transaction Type", income_types["income_types"])

    comments = st.text_area("Comments", placeholder="Add any additional details about the transaction...")

    submitted = st.form_submit_button("Submit")

    if submitted:
        fault = any(i is None or i == "" for i in [transaction_date, income_amount, currency, transaction_type])
        if fault:
            st.warning("There is an error in the form")
        else:
            submitting(["income", income_amount, currency, transaction_date, transaction_type, comments])
            st.success(f"You have entered an income amount of {income_amount:.2f} {currency} on {transaction_date.strftime('%d/%m/%Y')} for {transaction_type}. Comments: {comments}")