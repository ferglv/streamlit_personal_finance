# db/base_class.py
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import DeclarativeMeta


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    metadata: DeclarativeMeta
