# components/expenses/tabs/insert_tab.py
from datetime import datetime
from typing import Type

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session
from streamlit.runtime.uploaded_file_manager import UploadedFile

from db.base_class import Base
from db.crud import create, get_all, get_by_field
from db.database import SessionLocal
from db.schemas_tables import (
    ExpenseCategory,
    ExpenseSubcategory,
    ExpenseTransaction,
    ExpenseType,
    PaymentMethod,
)


def expenses_insert_tab() -> None:
    """
    Renders the UI components for inserting new expense transactions and uploading expense files.
    """
    with st.expander("Insert Expense"):
        insert_expenses_ui()

    with st.expander("Upload Expenses File"):
        upload_expenses_ui()


def insert_expenses_ui() -> None:
    """
    Handles the user interface and logic for inserting new expense transactions.
    """
    with SessionLocal() as session:
        category_options = get_select_options(session, ExpenseCategory)
        payment_method_options = get_select_options(session, PaymentMethod)
        expense_type_options = get_select_options(session, ExpenseType)

        selected_category_id, selected_subcategory_id, date = expense_details_input(
            session, category_options
        )
        payment_method_id, expense_type_id, invoice_requested = payment_details_input(
            payment_method_options, expense_type_options
        )
        (
            main_establishment,
            location,
            total,
            items,
            additional_info,
        ) = additional_expense_details()

        if st.button("Submit"):
            submit_expense(
                session,
                selected_category_id,
                selected_subcategory_id,
                payment_method_id,
                expense_type_id,
                main_establishment,
                location,
                total,
                items,
                additional_info,
                date,
                invoice_requested,
            )
            st.success("Expense transaction added successfully.")


def expense_details_input(
    session: Session, category_options: dict
) -> tuple[int, int, datetime]:
    """
    Creates input widgets for expense details such as category, subcategory, and date.

    Args:
        session (Session): The database session.
        category_options (dict): Dictionary of category options.

    Returns:
        tuple[int, int, datetime]: Tuple containing the selected category ID, subcategory ID, and date.
    """
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_category_id = category_select_ui(category_options)
    with col2:
        subcategory_options = get_subcategory_options(session, selected_category_id)
        selected_subcategory_id = subcategory_select_ui(subcategory_options)
    with col3:
        date = date_ui()
    return selected_category_id, selected_subcategory_id, date


def payment_details_input(
    payment_method_options: dict, expense_type_options: dict
) -> tuple[int, int, bool]:
    """
    Creates input widgets for payment details such as payment method and expense type.

    Args:
        payment_method_options (dict): Dictionary of payment method options.
        expense_type_options (dict): Dictionary of expense type options.

    Returns:
        tuple[int, int, bool]: Tuple containing the selected payment method ID, expense type ID, and invoice request flag.
    """
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        payment_method_id = select_ui("Payment Method", payment_method_options)
    with col2:
        expense_type_id = select_ui("Expense Type", expense_type_options)
    with col3:
        space_height = 35
        st.markdown(
            f"<div style='height: {space_height}px;'></div>", unsafe_allow_html=True
        )
        invoice_requested = st.checkbox("Invoice Requested", value=False)
    return payment_method_id, expense_type_id, invoice_requested


def additional_expense_details() -> tuple[str, str, float, str, str]:
    """
    Creates input widgets for additional expense details such as vendor, location, items, and notes.

    Returns:
        tuple[str, str, float, str, str]: Tuple containing main establishment, location, total amount, items, and additional information.
    """
    col1, col2 = st.columns([2, 2])
    with col1:
        main_establishment = st.text_input("Main Establishment")
    with col2:
        location = st.text_input("Location")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        items = st.text_input("Items")
    with col2:
        additional_info = st.text_input("Additional Information")
    with col3:
        total = st.number_input("Total", min_value=0.0, format="%.2f")
    return main_establishment, location, total, items, additional_info


def submit_expense(
    session: Session,
    category_id: int,
    subcategory_id: int,
    payment_method_id: int,
    expense_type_id: int,
    vendor: str,
    location: str,
    amount: float,
    description: str,
    additional_info: str,
    date: datetime,
    invoice_flag: bool,
) -> None:
    """
    Submits a new expense transaction to the database.

    Args:
        session (Session): The database session.
        category_id (int): ID of the selected category.
        subcategory_id (int): ID of the selected subcategory.
        payment_method_id (int): ID of the selected payment method.
        expense_type_id (int): ID of the selected expense type.
        vendor (str): Name of the vendor or establishment.
        location (str): Location of the expense.
        amount (float): Total amount of the expense.
        description (str): Description of the expense.
        additional_info (str): Additional information or notes.
        date (datetime): Date of the expense.
        invoice_flag (bool): Flag indicating if an invoice was requested.
    """
    data = {
        "date": date,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "payment_method_id": payment_method_id,
        "expense_type_id": expense_type_id,
        "vendor": vendor,
        "location": location,
        "description": description,
        "amount": amount,
        "invoice_flag": invoice_flag,
        "notes": additional_info,
    }
    create(session, ExpenseTransaction, data)


def upload_expenses_ui() -> None:
    """
    Creates the UI for uploading expenses file.
    """
    st.write("Upload your expenses file here (CSV).")
    uploaded_file = st.file_uploader("Choose a file", type=["csv"])
    if st.button("Process File") and uploaded_file:
        process_uploaded_file(uploaded_file)


def process_uploaded_file(uploaded_file: UploadedFile) -> None:
    """
    Processes the uploaded CSV file for expense transactions.

    Args:
        uploaded_file (UploadedFile): The uploaded CSV file.
    """
    df = pd.read_csv(uploaded_file)
    if df is not None:
        with SessionLocal() as session:
            results = create_expense_transactions_from_file(session, df)
            display_upload_results(results)


def create_expense_transactions_from_file(session: Session, df: pd.DataFrame) -> dict:
    """
    Creates expense transactions from a DataFrame.

    Args:
        session (Session): The database session.
        df (pd.DataFrame): DataFrame containing expense transaction data.

    Returns:
        dict: Dictionary with counts of successful and failed transaction insertions.
    """
    results = {"success": 0, "failed": 0}
    for _, row in df.iterrows():
        try:
            data = prepare_transaction_data(session, row)
            create(session, ExpenseTransaction, data)
            results["success"] += 1
        except Exception as e:
            st.error(f"Error in row {_}: {e}")
            results["failed"] += 1
    return results


def display_upload_results(results: dict) -> None:
    """
    Displays the results of the CSV file processing.

    Args:
        results (dict): Dictionary containing counts of successful and failed transactions.
    """
    st.success(f"Processed: {results['success']} transactions successfully.")
    st.error(f"Failed: {results['failed']} transactions.")


def prepare_transaction_data(session: Session, row: pd.Series) -> dict:
    """
    Prepares the transaction data from a row in DataFrame.

    Args:
        session (Session): The database session.
        row (pd.Series): A series representing a row in the DataFrame.

    Returns:
        dict: A dictionary of transaction data ready to be inserted into the database.
    """
    category_id = get_id_for_name(session, ExpenseCategory, row["category_name"])
    subcategory_id = get_id_for_name(
        session, ExpenseSubcategory, row["subcategory_name"]
    )
    payment_method_id = get_id_for_name(
        session, PaymentMethod, row["payment_method_name"]
    )
    expense_type_id = get_id_for_name(session, ExpenseType, row["expense_type_name"])
    return {
        "date": pd.to_datetime(row["date"]).date(),
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "payment_method_id": payment_method_id,
        "expense_type_id": expense_type_id,
        "vendor": row["vendor"],
        "location": row["location"],
        "description": row["description"],
        "amount": float(row["amount"]),
        "invoice_flag": row["invoice_flag"] == "True",
        "notes": row["notes"],
    }


def get_select_options(session: Session, model: Type[Base]) -> dict:
    """
    Retrieves and formats options for a select box from a given database model.

    Args:
        session (Session): The database session.
        model (Type[Base]): The SQLAlchemy model class.

    Returns:
        dict: Dictionary of ID to name mappings for the given model.
    """

    records = get_all(session, model)
    return {record.id: record.name for record in records}


def get_subcategory_options(session: Session, category_id: int) -> dict:
    """
    Retrieves and formats subcategory options based on the selected category.

    Args:
        session (Session): The database session.
        category_id (int): ID of the selected category.

    Returns:
        dict: Dictionary of subcategory ID to name mappings.
    """
    subcategories = get_by_field(
        session, ExpenseSubcategory, "category_id", category_id
    )
    return {sc.id: sc.name for sc in subcategories}


def category_select_ui(category_options: dict) -> int:
    """
    Creates a select box UI for choosing a category.

    Args:
        category_options (dict): Dictionary of category options.

    Returns:
        int: The selected category ID.
    """
    selected_category_id = st.selectbox(
        "Category",
        list(category_options.keys()),
        format_func=lambda x: category_options[x],
    )
    st.session_state["selected_category_id"] = selected_category_id
    return selected_category_id


def subcategory_select_ui(subcategory_options: dict) -> int:
    """
    Creates a select box UI for choosing a subcategory.

    Args:
        subcategory_options (dict): Dictionary of subcategory options.

    Returns:
        int: The selected subcategory ID.
    """
    selected_subcategory_id = st.selectbox(
        "SubCategory",
        list(subcategory_options.keys()),
        format_func=lambda x: subcategory_options[x],
    )
    return selected_subcategory_id


def date_ui() -> datetime:
    """
    Creates a date input UI.

    Returns:
        datetime: The selected date.
    """
    return st.date_input("Date", datetime.today())


def select_ui(title: str, options: dict) -> int:
    """
    Creates a select box UI for various options.

    Args:
        title (str): The title of the select box.
        options (dict): Dictionary of options for the select box.

    Returns:
        int: The selected option ID.
    """
    return st.selectbox(title, list(options.keys()), format_func=lambda x: options[x])


def get_id_for_name(session: Session, model: Type[Base], name: str) -> int:
    """
    Fetches the ID corresponding to the given name from the specified model.

    Args:
        session (Session): The database session.
        model (Type[Base]): The SQLAlchemy model class.
        name (str): Name whose ID is to be fetched.

    Returns:
        int: ID of the record with the given name.
    """
    record = session.query(model).filter(model.name == name).first()
    return record.id if record else None
