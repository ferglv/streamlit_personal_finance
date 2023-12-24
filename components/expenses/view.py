# components/expenses/view.py
import streamlit as st

from components.expenses.tabs.insert_tab import expenses_insert_tab


def expenses_view() -> None:
    """
    Renders the expenses view, including the dashboard and insert tabs.
    """
    st.title("Expenses")
    tab1, tab2 = st.tabs(["Expenses Dashboard", "Insert Expenses"])

    with tab1:
        # TODO: Expenses Dashboard
        st.write("Expenses Dashboard")

    with tab2:
        expenses_insert_tab()
