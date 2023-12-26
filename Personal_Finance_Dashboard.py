import streamlit as st
from dotenv import load_dotenv

from backend.helpers.session_state import keep_app_session

load_dotenv()

page_name = "Personal Finance App"
st.set_page_config(page_title=page_name, layout="wide")

st.title("Personal Finance Dashboard")
keep_app_session()


if __name__ == "__main__":
    pass
