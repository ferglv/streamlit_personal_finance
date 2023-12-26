# backend/helpers/table_generator.py
from typing import Any, Callable, Dict, Optional, Tuple, Type

import pandas as pd
import streamlit as st

from components.expenses.display_table import display_expenses_table
from components.incomes.display_table import display_payroll_table
from db.database import SessionLocal
from queries.query import Query


def prepare_data(
    session_factory: Callable[..., SessionLocal],
    query_object: Query,
    date_columns: list[str],
    catalogs: Dict[str, Type],
) -> pd.DataFrame:
    """
    Prepares data by executing a database query, converting specified columns to datetime,
    and replacing IDs with names from catalog tables.

    Args:
        session_factory: A factory function to create new database sessions.
        query_object: An object representing a database query.
        date_columns: List of column names to be converted to datetime.
        catalogs: Dictionary mapping column names to SQLAlchemy model classes.

    Returns:
        A pandas DataFrame with processed data.
    """
    data = query_object.execute_query()
    data[date_columns] = data[date_columns].apply(pd.to_datetime)
    return replace_ids_with_catalog_names(session_factory, data, catalogs)


def replace_ids_with_catalog_names(
    session_factory: Callable[..., SessionLocal],
    df: pd.DataFrame,
    catalogs: Dict[str, Type],
) -> pd.DataFrame:
    """
    Replaces ID values in specified columns with corresponding names from catalog tables.

    Args:
        session_factory: A factory function to create new database sessions.
        df: DataFrame containing data with IDs to replace.
        catalogs: Dictionary mapping column names to SQLAlchemy model classes.

    Returns:
        A DataFrame with IDs replaced by names.
    """
    with session_factory() as session:
        for id_column, model in catalogs.items():
            catalog_df = pd.read_sql(session.query(model).statement, session.bind)
            name_map = dict(zip(catalog_df["id"], catalog_df["name"]))
            df[id_column] = df[id_column].map(name_map).fillna(df[id_column])
    return df


def render_filters(
    session_factory: Callable[..., SessionLocal],
    data: pd.DataFrame,
    date_column: str,
    additional_filters: Optional[Dict[str, Callable[[SessionLocal], Any]]] = None,
) -> Tuple[Dict[str, Any], Tuple[st.columns, st.columns]]:
    """
    Renders filters in the Streamlit app and collects their values.

    Args:
        session_factory: A factory function to create new database sessions.
        data: DataFrame containing the data to be filtered.
        date_column: Name of the column containing date information.
        additional_filters: Dictionary of additional filter functions, if any.

    Returns:
        A tuple containing a dictionary of filter values and a tuple of Streamlit columns.
    """
    filters = {}

    years = ["All"] + sorted(data[date_column].dt.year.unique(), reverse=True)
    months = ["All"] + list(range(1, 13))

    col1, col2, col3, col4 = st.columns([0.2, 0.3, 0.3, 0.2])
    with col1:
        selected_year = st.selectbox(
            "Select Year",
            years,
            index=0,
            format_func=lambda x: "All" if x == "All" else str(x),
            key="selected_year",
        )
    with col2:
        selected_month = st.selectbox(
            "Select Month",
            months,
            index=0,
            format_func=lambda x: "All"
            if x == "All"
            else pd.to_datetime(f"1900-{x}-01").strftime("%B"),
            key="selected_month",
        )

    filters["year"] = selected_year
    filters["month"] = selected_month

    if additional_filters:
        for filter_name, filter_func in additional_filters.items():
            filters[filter_name] = filter_func(session_factory)

    return filters, (col3, col4)


def apply_filters(
    data: pd.DataFrame, filters: Dict[str, Any], date_column: str
) -> pd.DataFrame:
    """
    Applies the specified filters to the DataFrame.

    Args:
        data: DataFrame to be filtered.
        filters: Dictionary of filters to apply.
        date_column: Name of the column containing date information.

    Returns:
        A filtered DataFrame.
    """
    if filters["year"] != "All":
        data = data[data[date_column].dt.year == filters["year"]]
    if filters["month"] != "All":
        data = data[data[date_column].dt.month == filters["month"]]
    if "category_filter" in filters:
        data = data[data["category_id"].isin(filters["category_filter"])]

    return data


def display_table(
    data: pd.DataFrame,
    table_type: str,
    col3: st.delta_generator.DeltaGenerator,
    col4: st.delta_generator.DeltaGenerator,
) -> None:
    """
    Displays a table with pagination in the Streamlit app.

    Args:
        data: Data to display in the table.
        table_type: Type of the table (e.g., 'expenses', 'payroll').
        col3: Streamlit column for pagination controls.
        col4: Streamlit column for pagination details.
    """
    page_size = int(st.session_state.get("page_size", 10))
    total_rows = len(data)
    num_pages = (total_rows // page_size) + (1 if total_rows % page_size > 0 else 0)

    with col3:
        selected_page = st.number_input(
            "Page", min_value=1, max_value=max(1, num_pages), step=1, value=1
        )
    with col4:
        space_height = 35
        st.markdown(
            f"<div style='height: {space_height}px;'></div>", unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: left;'>Page <strong>{selected_page}</strong> of <strong>{max(1, num_pages)}</strong></div>",
            unsafe_allow_html=True,
        )

    start_row = (selected_page - 1) * page_size
    end_row = start_row + page_size
    paginated_data = data.iloc[start_row:end_row]

    if table_type == "expenses":
        display_expenses_table(paginated_data)
    else:
        st.error(f"Unsupported table type: {table_type}")
