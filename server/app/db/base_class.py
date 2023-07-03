import typing as t

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
