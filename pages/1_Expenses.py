# pages/1_Expenses.py
import streamlit as st

from backend.helpers.session_state import keep_app_session
from components.expenses.view import expenses_view


def main() -> None:
    """
    Main function to render the expenses view in the Streamlit app.
    """
    page_name = "Expenses App"
    st.set_page_config(page_title=page_name, layout="wide")
    keep_app_session()
    expenses_view()


if __name__ == "__main__":
    main()
