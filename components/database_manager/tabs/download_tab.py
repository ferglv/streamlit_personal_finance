# components/database_manager/tabs/download_tab.py
import os
from datetime import datetime

import streamlit as st

from components.database_manager.authentication import authenticate_user
from components.database_manager.utils import db_exists
from components.database_manager.utils import get_project_root


def database_manager_download_tab() -> None:
    db_file_name = os.getenv("DB_NAME")
    if db_exists(db_file_name):
        if authenticate_user("download"):
            st.subheader("Download Database")
            download_db(db_file_name)
    else:
        st.error("Database file not found.")


def download_db(db_file_name: str) -> None:
    db_path = os.path.join(get_project_root(), db_file_name)
    with open(db_path, "rb") as file:
        st.download_button(
            label="Download SQLite Database",
            data=file,
            file_name=f"{db_file_name[:-3]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            mime="application/octet-stream",
        )
