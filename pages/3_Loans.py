# pages/3_Loans.py
import streamlit as st

from backend.helpers.session_state import keep_app_session


def main():
    st.title("Loans Page")
    keep_app_session()


if __name__ == "__main__":
    main()
