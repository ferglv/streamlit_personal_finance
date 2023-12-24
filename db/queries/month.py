import pandas as pd

from db.database import SessionLocal
from db.schemas_tables import Month  # Assuming Month is your table model


def fetch_months_data(session: SessionLocal) -> pd.DataFrame:
    """
    Fetches month data from the database.

    Args:
        session (SessionLocal): Database session for querying the data.

    Returns:
        pd.DataFrame: DataFrame containing month data.
    """
    months_query = session.query(Month).order_by(Month.id)
    return pd.read_sql(months_query.statement, session.bind)
