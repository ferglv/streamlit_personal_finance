# pages/5_Database_Manager.py
import streamlit as st

from backend.helpers.session_state import keep_app_session
from components.database_manager.view import database_manager_view


def main():
    page_name = "Database Manager App"
    st.set_page_config(page_title=page_name, layout="wide")
    keep_app_session()
    database_manager_view()


if __name__ == "__main__":
    main()
