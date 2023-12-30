import os
from datetime import date

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from formatters.formatter import CategoryListFormatter
from queries.category import QueryCategory

load_dotenv()


def keep_app_session() -> None:
    """
    Initializes or retains session state for selected year, month, and categories
    in a Streamlit app, ensuring persistence across pages.
    """
    current_year, current_month = date.today().year, date.today().month
    st.session_state.setdefault("selected_year", current_year)
    st.session_state.setdefault("selected_month", current_month)
    st.session_state.setdefault("rows_per_page", 5)

    if "selected_categories" not in st.session_state:
        session_factory = session_state_session()
        formatter = CategoryListFormatter()
        query_category = QueryCategory(session_factory, formatter)
        categories = query_category.execute_query()
        st.session_state["selected_categories"] = categories

    if st.session_state["rows_per_page"]:
        st.session_state["rows_per_page"] = st.session_state["rows_per_page"]

    if st.session_state["selected_year"]:
        st.session_state["selected_year"] = st.session_state["selected_year"]

    if st.session_state["selected_month"]:
        st.session_state["selected_month"] = st.session_state["selected_month"]

    if st.session_state["selected_categories"]:
        st.session_state["selected_categories"] = st.session_state[
            "selected_categories"
        ]


def session_state_session() -> sessionmaker:
    """
    Creates and returns a SQLAlchemy sessionmaker bound to an engine.

    Returns:
        A sessionmaker instance for database operations.
    """
    engine = create_engine(f"sqlite:///{os.getenv('DB_NAME')}", pool_pre_ping=True)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
