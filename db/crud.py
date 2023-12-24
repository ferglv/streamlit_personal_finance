# db/crud.py
from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.sql import sqltypes

from db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


def get_all(
    db: Session, model: Type[ModelType], skip: int = 0, limit: int = 100
) -> list[ModelType]:
    """
    Retrieve a list of records from the database.

    :param db: Database session.
    :param model: SQLAlchemy model class.
    :param skip: Number of records to skip (for pagination).
    :param limit: Maximum number of records to return.
    :return: List of model instances.
    """
    return db.query(model).offset(skip).limit(limit).all()


def get_by_field(
    db: Session,
    model: Type[ModelType],
    field_name: str,
    field_value: Any,
    skip: int = 0,
    limit: int = 100,
) -> List[ModelType]:
    """
    Retrieve records from the database based on a specific field's value.

    :param db: Database session.
    :param model: SQLAlchemy model class.
    :param field_name: Name of the field to filter by.
    :param field_value: Value of the field to filter by.
    :param skip: Number of records to skip (for pagination).
    :param limit: Maximum number of records to return.
    :return: List of model instances matching the field criteria.
    """
    mapper = inspect(model)
    if field_name not in mapper.attrs:
        raise ValueError(f"Field '{field_name}' not found in model '{model.__name__}'.")

    column = getattr(model, field_name)
    if not isinstance(column.expression.type, sqltypes.TypeEngine):
        raise TypeError(f"Field '{field_name}' is not a valid SQLAlchemy column.")

    return db.query(model).filter(column == field_value).offset(skip).limit(limit).all()


def create(db: Session, model: Type[ModelType], obj_in: dict) -> ModelType:
    """
    Create a new record in the database.

    :param db: Database session.
    :param model: SQLAlchemy model class.
    :param obj_in: Dictionary containing the data for the new record.
    :return: The newly created model instance.
    """
    obj = model(**obj_in)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(
    db: Session, model: Type[ModelType], obj_id: Any, obj_in: dict
) -> Optional[ModelType]:
    """
    Update an existing record in the database.

    :param db: Database session.
    :param model: SQLAlchemy model class.
    :param obj_id: ID of the object to update.
    :param obj_in: Dictionary containing fields to update.
    :return: The updated model instance or None if not found.
    """
    obj = db.query(model).filter(model.id == obj_id).first()
    if obj:
        for var, value in obj_in.items():
            setattr(obj, var, value) if value else None
        db.commit()
        db.refresh(obj)
        return obj
    return None


def delete(db: Session, model: Type[ModelType], obj_id: Any) -> Optional[ModelType]:
    """
    Delete a record from the database.

    :param db: Database session.
    :param model: SQLAlchemy model class.
    :param obj_id: ID of the object to delete.
    :return: The deleted model instance or None if not found.
    """
    obj = db.query(model).get(obj_id)
    if obj:
        db.delete(obj)
        db.commit()
        return obj
    return None
