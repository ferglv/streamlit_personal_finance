# components/database_manager/authentication.py
import os

import streamlit as st


def authenticate_user(action: str) -> bool:
    """
    Authenticates the user for a given action (download or upload).

    Args:
    action (str): The action requiring authentication.

    Returns:
    bool: True if authentication is successful, False otherwise.
    """
    password = st.text_input(
        f"Enter the password to {action}", type="password", key=f"{action}_pwd"
    )
    secret_password = os.getenv("DB_PASSWORD")
    return password and secret_password and password == secret_password
