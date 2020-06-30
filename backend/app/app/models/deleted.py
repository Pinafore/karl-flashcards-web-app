from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from .fact import Fact
from .user import User


class Deleted(Base):
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_deleted = Column(TIMESTAMP(timezone=True), nullable=False)

    deleter = relationship("User", backref=backref("deletions", cascade="all, delete-orphan"))
    deleted_fact = relationship("Fact", backref=backref("deletions", cascade="all, delete-orphan"))

    def __init__(self, deleter: User, deleted_fact: Fact, date_deleted: datetime):
        self.deleted_fact = deleted_fact
        self.deleter = deleter
        self.date_deleted = date_deleted
