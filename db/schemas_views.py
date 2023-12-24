# db/schemas_views.py
from sqlalchemy import Column, Integer, String

from db.base_class import Base


class CategorySubcategoryView(Base):
    __tablename__ = "category_subcategory_view"
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String)
    subcategory_name = Column(String)
