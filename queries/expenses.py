from typing import Any

from sqlalchemy import desc, exc
from sqlalchemy.orm import sessionmaker

from db.schemas_tables import ExpenseTransaction
from formatters.formatter import Formatter
from queries.query import Query


class QueryExpenses(Query):
    def __init__(
        self,
        session_factory: sessionmaker,
        formatter: Formatter,
        owner_id: int = 1,
        type_id: int = 1,
    ) -> None:
        """
        Initialize the QueryExpenses instance.

        Args:
            session_factory: A factory to create new database sessions.
            formatter: An instance of a formatter to format the query results.
            owner_id: Owner's identifier for filtering expenses.
            type_id: Type identifier for filtering expenses.
        """
        super().__init__(session_factory)
        self.formatter = formatter
        self.owner_id = owner_id
        self.type_id = type_id

    def execute_query(self) -> Any:
        """
        Executes a query to fetch expenses transactions based on owner and type.

        Returns:
            Formatted query results.

        Raises:
            RuntimeError: If an error occurs during the database query or formatting.
        """
        try:
            with self.session_factory() as session:
                expenses_query = (
                    session.query(ExpenseTransaction)
                    .filter(ExpenseTransaction.owner_id == self.owner_id)
                    .filter(ExpenseTransaction.type_id == self.type_id)
                    .order_by(desc(ExpenseTransaction.date))
                )
                expenses_data = expenses_query.all()
                return self.formatter.format(expenses_data)
        except exc.SQLAlchemyError as e:
            raise RuntimeError("An error occurred while fetching expenses data.") from e
        except Exception as e:
            raise RuntimeError("An unexpected error occurred in QueryExpenses.") from e
