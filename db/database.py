# db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base_class import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///personal_finance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)
