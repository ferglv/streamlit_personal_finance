import pandas as pd
import streamlit as st


def display_expenses_table(data: pd.DataFrame) -> None:
    """
    Displays the formatted expenses table in the Streamlit app.

    Args:
        data (pd.DataFrame): Data containing expense information.
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
    }

    if "id" in data.columns:
        data.set_index("id", inplace=True)

    st.dataframe(
        data,
        column_order=column_order,
        column_config=column_config,
        use_container_width=True,
    )
