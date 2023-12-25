# components/database_manager/view.py
import streamlit as st

from components.database_manager.tabs.download_tab import database_manager_download_tab
from components.database_manager.tabs.upload_tab import database_manager_upload_tab


def database_manager_view() -> None:
    """
    Renders the database manager view, including the download database and upload database tabs.
    """
    st.title("Database Manager")
    tab1, tab2 = st.tabs(["Download Database", "Upload Database"])

    with tab1:
        database_manager_download_tab()

    with tab2:
        database_manager_upload_tab()
