# components/database_manager/utils.py
import os


def get_project_root() -> str:
    """
    Finds and returns the absolute path to the project's root directory, 'streamlit_personal_finance'.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while True:
        parent_dir = os.path.dirname(current_dir)
        if os.path.basename(parent_dir) == '':
            raise Exception("Project root folder 'streamlit_personal_finance' not found.")
        if os.path.basename(parent_dir) == 'streamlit_personal_finance':
            return parent_dir
        current_dir = parent_dir


def db_exists(db_file_name: str) -> bool:
    """
    Checks if the specified database file exists in the project root directory.

    Args:
        db_file_name (str): The name of the database file.

    Returns:
        bool: True if the database file exists, False otherwise.
    """
    project_root_dir = get_project_root()
    db_files = [f for f in os.listdir(project_root_dir) if f.endswith('.db') and f == db_file_name]
    return bool(db_files)
