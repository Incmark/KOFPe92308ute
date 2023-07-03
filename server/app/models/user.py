from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    status_purchased_time = Column(DateTime)
    status_id = Column(Integer, ForeignKey(
        'status.id'))
    status = relationship('Status', foreign_keys=[
        status_id], uselist=False)
