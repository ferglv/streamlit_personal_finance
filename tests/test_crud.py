# tests/test_crud.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base_class import Base
from db.crud import create, delete, get_all, get_by_field, update
from db.schemas_tables import ExpenseCategory

# Configure test database (using in-memory SQLite for this example)
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for a test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()


def test_create_category(db_session):
    category_data = {"name": "Test Create Category"}
    category = create(db_session, ExpenseCategory, category_data)
    assert category.id is not None
    assert category.name == "Test Create Category"


def test_get_all_categories(db_session):
    # Create test data
    create(db_session, ExpenseCategory, {"name": "Test Read Category 1"})
    create(db_session, ExpenseCategory, {"name": "Test Read Category 2"})

    categories = get_all(db_session, ExpenseCategory)
    assert len(categories) >= 2


def test_get_category_by_field(db_session):
    category_name = "Test Read Category Field"
    create(db_session, ExpenseCategory, {"name": category_name})

    categories = get_by_field(db_session, ExpenseCategory, "name", category_name)
    assert len(categories) == 1
    assert categories[0].name == category_name


def test_update_category(db_session):
    category_data = {"name": "Category Before Update"}
    category = create(db_session, ExpenseCategory, category_data)
    updated_data = {"name": "Updated Category"}
    updated_category = update(db_session, ExpenseCategory, category.id, updated_data)

    assert updated_category is not None
    assert updated_category.name == "Updated Category"


def test_delete_category(db_session):
    category_data = {"name": "Category to Delete"}
    category = create(db_session, ExpenseCategory, category_data)
    deleted_category = delete(db_session, ExpenseCategory, category.id)

    assert deleted_category is not None
    remaining_categories = get_all(db_session, ExpenseCategory)
    assert all(cat.name != "Category to Delete" for cat in remaining_categories)
