from abc import ABC, abstractmethod
from typing import Any, List

import pandas as pd


class Formatter(ABC):
    @abstractmethod
    def format(self, data: Any) -> Any:
        """
        Abstract method to format data. Must be implemented by subclasses.

        Args:
            data: The data to be formatted.

        Returns:
            The formatted data.
        """
        pass


class ObjectFormatter(Formatter):
    def format(self, data: Any) -> Any:
        """
        Returns the data as-is, without any formatting.

        Args:
            data: The data to be formatted.

        Returns:
            The original data.
        """
        return data


class CategoryListFormatter(Formatter):
    def format(self, data: List[Any]) -> List[str]:
        """
        Formats a list of category objects into a list of category names.

        Args:
            data: A list of category objects.

        Returns:
            A list of category names.
        """
        return [category.name for category in data]


class ExpenseDataFrameFormatter(Formatter):
    def format(self, data: List[Any]) -> pd.DataFrame:
        """
        Formats expense data into a pandas DataFrame.

        Args:
            data: A list of expense objects.

        Returns:
            A pandas DataFrame with detailed expense information.
        """
        expense_records = [
            {
                "id": item.id,
                "category_id": item.category_id,
                "subcategory_id": item.subcategory_id,
                "expense_type_id": item.expense_type_id,
                "payment_method_id": item.payment_method_id,
                "amount": item.amount,
                "tax": item.tax,
                "invoice_flag": item.invoice_flag,
                "date": item.date,
                "vendor": item.vendor,
                "location": item.location,
                "description": item.description,
                "notes": item.notes,
            }
            for item in data
        ]
        return pd.DataFrame(expense_records)
