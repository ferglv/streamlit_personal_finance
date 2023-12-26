from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from db.schemas_tables import ExpenseCategory
from formatters.formatter import Formatter
from logger.logger import logger
from queries.query import Query


class QueryCategory(Query):
    def __init__(self, session_factory: sessionmaker, formatter: Formatter) -> None:
        """
        Initialize the QueryCategory instance.

        Args:
            session_factory: A factory to create new database sessions.
            formatter: An instance of a formatter to format the query results.
        """
        super().__init__(session_factory)
        self.formatter = formatter

    def execute_query(self) -> Any:
        """
        Executes a query to fetch expense categories and formats the results.

        Returns:
            Formatted query results.

        Raises:
            RuntimeError: If an error occurs during the database query or formatting.
        """
        try:
            with self.session_factory() as session:
                categories = (
                    session.query(ExpenseCategory).order_by(ExpenseCategory.id).all()
                )
                return self.formatter.format(categories)
        except SQLAlchemyError as e:
            logger.error(f"Database error in QueryCategory: {e}")
            raise RuntimeError(
                "An error occurred while fetching categories data."
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error in QueryCategory: {e}")
            raise RuntimeError("An unexpected error occurred in QueryCategory.") from e
