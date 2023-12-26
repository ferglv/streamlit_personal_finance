from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import sessionmaker


class Query(ABC):
    def __init__(self, session_factory: sessionmaker) -> None:
        """
        Initializes a new Query instance with a given session factory.

        Args:
            session_factory: A factory function for creating new database session instances.
        """
        self.session_factory = session_factory

    @abstractmethod
    def execute_query(self) -> Any:
        """
        Abstract method to execute a specific database query.

        This method should be implemented by subclasses to define specific query logic.

        Returns:
            The result of the executed query, the format of which will depend on the subclass implementation.
        """
        pass
