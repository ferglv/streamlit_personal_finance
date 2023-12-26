# pages/2_Incomes.py
import streamlit as st

from backend.helpers.session_state import keep_app_session


def main():
    st.title("Incomes Page")
    keep_app_session()


if __name__ == "__main__":
    main()
