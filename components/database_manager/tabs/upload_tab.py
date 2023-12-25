# components/database_manager/tabs/upload_tab.py
import os
import streamlit as st

from components.database_manager.authentication import authenticate_user
from components.database_manager.utils import db_exists
from components.database_manager.utils import get_project_root


def database_manager_upload_tab() -> None:
    db_file_name = os.getenv("DB_NAME")
    if authenticate_user("upload"):
        st.subheader("Upload Database")
        upload_db(db_file_name)


def upload_db(db_file_name: str) -> None:
    uploaded_file = st.file_uploader("Upload SQLite database", type=["db"])
    if uploaded_file is not None:
        if uploaded_file.name == db_file_name:
            db_path = os.path.join(get_project_root(), db_file_name)
            try:
                with open(db_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Database uploaded successfully.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Incorrect DB File Name. Please upload the correct file.")
    elif db_exists(db_file_name):
        st.warning("No file uploaded. Existing database remains unchanged.")
    else:
        st.error("No database exists and no file uploaded.")
