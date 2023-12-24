import os
from typing import Any, Dict, List, Tuple, Type

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.queries.categories import fetch_categories_data
from db.queries.expenses import fetch_expenses_data
from db.queries.month import fetch_months_data
from db.schemas_tables import (
    ExpenseCategory,
    ExpenseSubcategory,
    ExpenseType,
    PaymentMethod,
)


def expenses_table_tab() -> None:
    """
    Renders tabs in the Streamlit app to display tables of expenses and summary pivot tables,
    with options to filter by a specific year and month, including pagination.
    """
    with SessionLocal() as session:
        expenses_data = prepare_expenses_data(session)
        months_df = fetch_months_data(session)
        year_filter, month_filter, selected_categories, col3, col4 = render_filters(
            expenses_data, session
        )
        filtered_data = apply_filters(
            expenses_data,
            int(year_filter),
            month_filter,
            months_df,
            selected_categories,
        )
        display_expenses_data(filtered_data, col3, col4)


def prepare_expenses_data(session: Session) -> pd.DataFrame:
    """
    Fetches and prepares expenses data for display.

    Args:
        session (Session): Active database session.

    Returns:
        pd.DataFrame: DataFrame containing prepared expenses data.
    """
    expenses_data = fetch_expenses_data(session)
    expenses_data["date"] = pd.to_datetime(expenses_data["date"])
    return replace_ids_with_catalog_names(session, expenses_data)


def replace_ids_with_catalog_names(session: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces specific ID columns in the DataFrame with corresponding names from catalog tables.

    Args:
        session (Session): Database session for querying catalog data.
        df (pd.DataFrame): DataFrame where ID columns need to be replaced.

    Returns:
        pd.DataFrame: DataFrame with ID columns replaced by names.
    """
    df = df.copy()
    catalogs: Dict[str, Type] = {
        "payment_method_id": PaymentMethod,
        "expense_type_id": ExpenseType,
        "category_id": ExpenseCategory,
        "subcategory_id": ExpenseSubcategory,
    }
    for id_column, model in catalogs.items():
        catalog_df = pd.read_sql(session.query(model).statement, session.bind)
        name_map = dict(zip(catalog_df["id"], catalog_df["name"]))
        df[id_column] = df[id_column].map(name_map).fillna(df[id_column])
    return df


def render_filters(
    expenses_data: pd.DataFrame, session: Session
) -> Tuple[str, str, List[str], Any, Any]:
    """
    Renders year, month, category filters, and pagination information for expenses data.

    Args:
        expenses_data (pd.DataFrame): The expenses data.
        session (Session): Active database session.

    Returns:
        Tuple containing the selected year, month, categories, the column object for pagination,
        and the column for pagination info.
    """
    months_df, categories_df = fetch_filter_data(session)

    selected_year, selected_month, col3, col4 = render_year_month_pagination_filters(
        expenses_data, months_df
    )
    selected_categories = render_category_filter(categories_df)

    return selected_year, selected_month, selected_categories, col3, col4


def fetch_filter_data(session: Session) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetches data for month and category filters.

    Args:
        session (Session): Active database session.

    Returns:
        Tuple of DataFrames for months and categories.
    """
    months_df = fetch_months_data(session)
    categories_df = fetch_categories_data(session)
    return months_df, categories_df


def render_year_month_pagination_filters(
    expenses_data: pd.DataFrame, months_df: pd.DataFrame
) -> Tuple[str, str, Any, Any]:
    """
    Renders filters for selecting year and month along with pagination controls and pagination info.

    Args:
        expenses_data (pd.DataFrame): Expenses data for extracting years.
        months_df (pd.DataFrame): Data for months.

    Returns:
        Tuple of selected year, month, the column object for pagination, and the column for pagination info.
    """
    month_options = ["All"] + months_df["name"].tolist()
    years = sorted(expenses_data["date"].dt.year.unique(), reverse=True)

    col1, col2, col3, col4 = st.columns([0.2, 0.3, 0.3, 0.2])
    with col1:
        selected_year = st.selectbox("Select Year:", years, index=0)
    with col2:
        selected_month = st.selectbox("Select Month:", month_options, index=0)

    return selected_year, selected_month, col3, col4


def render_category_filter(categories_df: pd.DataFrame) -> List[str]:
    """
    Renders a multi-select filter for categories.

    Args:
        categories_df (pd.DataFrame): DataFrame containing categories data.

    Returns:
        List of selected categories.
    """
    categories_names = categories_df["name"].tolist()
    with st.expander("Categories Filters:"):
        selected_categories = st.multiselect(
            "Available Categories", options=categories_names, default=categories_names
        )

    return selected_categories


def apply_filters(
    expenses_data: pd.DataFrame,
    year: int,
    month: str,
    months_df: pd.DataFrame,
    selected_categories: List[str],
) -> pd.DataFrame:
    """
    Applies year, month, and category filters to expenses data.

    Args:
        expenses_data (pd.DataFrame): The expenses data.
        year (int): Selected year for filtering.
        month (str): Selected month for filtering.
        months_df (pd.DataFrame): DataFrame containing month names and IDs.
        selected_categories (List[str]): List of selected category names for filtering.

    Returns:
        pd.DataFrame: Filtered expenses data.
    """
    filtered_data = expenses_data[expenses_data["date"].dt.year == year]

    if month != "All":
        selected_month_index = months_df[months_df["name"] == month]["id"].iloc[0]
        filtered_data = filtered_data[
            filtered_data["date"].dt.month == selected_month_index
        ]

    filtered_data = filtered_data[
        filtered_data["category_id"].isin(selected_categories)
    ]

    return filtered_data


def display_expenses_data(filtered_data: pd.DataFrame, col3: Any, col4: Any) -> None:
    """
    Displays the expenses table and pivot tables with pagination in the Streamlit app.

    Args:
        filtered_data (pd.DataFrame): Filtered expenses data to be displayed.
        col3: Streamlit column object for pagination controls.
        col4: Streamlit column object for displaying pagination information.
    """
    page_size = int(os.getenv("PAGINATION_SIZE", 10))
    total_rows = len(filtered_data)
    num_pages = (total_rows // page_size) + (1 if total_rows % page_size > 0 else 0)

    with col3:
        selected_page = st.number_input(
            "Select Page", min_value=1, max_value=max(1, num_pages), step=1, value=1
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
    paginated_data = filtered_data.iloc[start_row:end_row]

    st.subheader("Expenses Table")
    display_expenses_table(paginated_data)

    display_pivot_tables(filtered_data)


def display_expenses_table(df: pd.DataFrame) -> None:
    """
    Displays a formatted expenses table in the Streamlit app.

    Args:
        df (pd.DataFrame): DataFrame containing expense data to be displayed.
    """
    column_order = [
        "id",
        "date",
        "vendor",
        "location",
        "description",
        "amount",
        "tax",
        "payment_method_id",
        "invoice_flag",
        "expense_type_id",
        "category_id",
        "subcategory_id",
        "notes",
    ]
    column_config = {
        "id": "Expense ID",
        "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "vendor": "Vendor",
        "location": "Location",
        "description": "Description",
        "amount": st.column_config.NumberColumn("Amount", min_value=0, format="$ %.2f"),
        "tax": st.column_config.NumberColumn("Tax", min_value=0, format="$ %.2f"),
        "payment_method_id": "Payment Method",
        "invoice_flag": "Invoice Requested",
        "expense_type_id": "Expense Type",
        "category_id": "Category",
        "subcategory_id": "Subcategory",
        "notes": "Notes",
        "created_at": None,
        "updated_at": None,
        "owner_id": None,
        "type_id": None,
    }

    if "id" in df.columns:
        df = df.set_index("id")

    st.dataframe(
        df,
        column_order=column_order,
        column_config=column_config,
        use_container_width=True,
    )


def display_pivot_tables(df: pd.DataFrame) -> None:
    """
    Generates and displays summary pivot tables in the Streamlit app.

    Args:
        df (pd.DataFrame): DataFrame containing expense data for pivot tables.
    """
    pivot_category = create_pivot_table(df, ["category_id"])
    pivot_category_subcategory = create_pivot_table(
        df, ["category_id", "subcategory_id"]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Summary by Category")
        display_pivot_table(pivot_category, ["category_id", "amount"])
    with col2:
        st.subheader("Summary by Category/Subcategory")
        display_pivot_table(
            pivot_category_subcategory, ["category_id", "subcategory_id", "amount"]
        )


def create_pivot_table(df: pd.DataFrame, group_by: List[str]) -> pd.DataFrame:
    """
    Creates a pivot table of expenses grouped by specified columns.

    Args:
        df (pd.DataFrame): DataFrame containing expense data.
        group_by (List[str]): Columns to group by in the pivot table.

    Returns:
        pd.DataFrame: Generated pivot table.
    """
    df = df.copy()
    df[group_by] = df[group_by].fillna("Unspecified")
    return df.groupby(group_by)["amount"].sum().reset_index().sort_values(by=group_by)


def display_pivot_table(pivot_df: pd.DataFrame, columns: List[str]) -> None:
    """
    Displays a pivot table in the Streamlit app.

    Args:
        pivot_df (pd.DataFrame): Pivot table DataFrame to be displayed.
        columns (List[str]): Columns to display in the pivot table.
    """
    column_order = columns
    column_config = {
        "category_id": st.column_config.TextColumn("Category"),
        "subcategory_id": st.column_config.TextColumn("Subcategory"),
        "amount": st.column_config.NumberColumn("Total Amount", format="$ %.2f"),
    }
    st.dataframe(
        pivot_df[column_order],
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )
