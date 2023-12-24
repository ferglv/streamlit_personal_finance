import pandas as pd
from sqlalchemy import desc

from db.database import SessionLocal
from db.schemas_tables import ExpenseTransaction


def fetch_expenses_data(
    session: SessionLocal, owner_id: int = 1, type_id: int = 1
) -> pd.DataFrame:
    """
    Fetches expense transaction data from the database, filtered by owner and type, and sorted in descending order.

    Args:
        session (SessionLocal): Database session for querying the data.
        owner_id (int): ID of the owner to filter the expenses. Default is 1.
        type_id (int): ID of the expense type to filter. Default is 1.

    Returns:
        pd.DataFrame: DataFrame containing the filtered and sorted expense transaction data.
    """
    expenses_query = (
        session.query(ExpenseTransaction)
        .filter(ExpenseTransaction.owner_id == owner_id)
        .filter(ExpenseTransaction.type_id == type_id)
        .order_by(desc(ExpenseTransaction.date))
    )
    return pd.read_sql(expenses_query.statement, session.bind)
