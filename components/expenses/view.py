# components/expenses/view.py
import streamlit as st

from components.expenses.tabs.insert_tab import expenses_insert_tab
from components.expenses.tabs.table_tab import expenses_table_tab


def expenses_view() -> None:
    """
    Renders the expenses view, including the dashboard, table and insert tabs.
    """
    st.title("Expenses")
    tab1, tab2, tab3 = st.tabs(
        ["Expenses Dashboard", "Expenses Table", "Insert Expenses"]
    )

    with tab1:
        # TODO: Expenses Dashboard
        st.write("Expenses Dashboard")

    with tab2:
        expenses_table_tab()

    with tab3:
        expenses_insert_tab()
