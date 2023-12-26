from typing import Dict, List, Type

import pandas as pd
import streamlit as st

from components.table_generator import (
    apply_filters,
    display_table,
    prepare_data,
    render_filters,
)
from db.database import SessionLocal
from db.schemas_tables import (
    ExpenseCategory,
    ExpenseSubcategory,
    ExpenseType,
    PaymentMethod,
)
from formatters.formatter import CategoryListFormatter, ExpenseDataFrameFormatter
from queries.category import QueryCategory
from queries.expenses import QueryExpenses


def expenses_table_tab() -> None:
    """
    Renders tabs in the Streamlit app to display tables of expenses and summary pivot tables,
    with options to filter by a specific year and month, including pagination.
    """
    session_factory = SessionLocal
    catalogs: Dict[str, Type] = {
        "payment_method_id": PaymentMethod,
        "expense_type_id": ExpenseType,
        "category_id": ExpenseCategory,
        "subcategory_id": ExpenseSubcategory,
    }
    formatter_expenses = ExpenseDataFrameFormatter()
    query_expenses = QueryExpenses(session_factory, formatter_expenses)

    expenses_data = prepare_data(session_factory, query_expenses, ["date"], catalogs)
    filters, (col3, col4) = render_filters(
        session_factory,
        expenses_data,
        "date",
        {"category_filter": render_category_filter},
    )
    filtered_data = apply_filters(expenses_data, filters, "date")
    display_table(filtered_data, "expenses", col3, col4)
    display_pivot_tables(filtered_data)


def render_category_filter(session_factory: SessionLocal) -> List[str]:
    """
    Renders a filter for selecting categories in the Streamlit app.

    Args:
        session_factory: A factory function to create new database sessions.

    Returns:
        A list of selected category names.
    """
    formatter_category = CategoryListFormatter()
    query_category = QueryCategory(session_factory, formatter_category)
    categories_names = query_category.execute_query()
    with st.expander("Categories Filters:"):
        selected_categories = st.multiselect(
            "Available Categories", options=categories_names, default=categories_names
        )

    return selected_categories


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
