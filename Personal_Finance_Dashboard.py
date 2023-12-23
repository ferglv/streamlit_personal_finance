import streamlit as st
from dotenv import load_dotenv

load_dotenv()

app_name = "Personal Finance App"
st.set_page_config(page_title=app_name, layout="wide")

st.title("Personal Finance Dashboard")


if __name__ == "__main__":
    pass
