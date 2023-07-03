from sqlalchemy import Column, Integer, String, Boolean, Interval

from app.db.base_class import Base

class Status(Base):
    id = Column(Integer, autoincrement=True, primary_key=True, index=False)
    name = Column(String, nullable=False)
    plan = Column(Interval, nullable=False)
    lifetime = Column(Boolean, nullable=False)
    services_enabled = Column(String, nullable=False)

    def __eq__(self, __o: object) -> bool:
        return (self.id == getattr(__o, 'id', object()) and self.__class__.__name__ == __o.__class__.__name__)