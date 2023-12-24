# pages/1_Expenses.py
from components.expenses.view import expenses_view


def main() -> None:
    """
    Main function to render the expenses view in the Streamlit app.
    """
    expenses_view()


if __name__ == "__main__":
    main()
