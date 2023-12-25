# db/database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from components.database_manager.utils import db_exists
from db.base_class import Base

db_file_name = os.getenv("DB_NAME")
if db_exists(db_file_name):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_file_name}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
