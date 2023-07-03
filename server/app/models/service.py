from sqlalchemy import Column, Integer, String

from app.db.base_class import Base

class Service(Base):
    id = Column(Integer, unique=True, primary_key=True, index=False)
    name = Column(String, unique=True, index=False)

    def __eq__(self, __o: object) -> bool:
        return (self.id == getattr(__o, 'id', object()) and self.__class__.__name__ == __o.__class__.__name__)