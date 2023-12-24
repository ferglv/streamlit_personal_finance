import pandas as pd

from db.database import SessionLocal
from db.schemas_tables import ExpenseCategory


def fetch_categories_data(session: SessionLocal) -> pd.DataFrame:
    """
    Fetches month data from the database.

    Args:
        session (SessionLocal): Database session for querying the data.

    Returns:
        pd.DataFrame: DataFrame containing month data.
    """
    categories_query = session.query(ExpenseCategory).order_by(ExpenseCategory.id)
    return pd.read_sql(categories_query.statement, session.bind)
