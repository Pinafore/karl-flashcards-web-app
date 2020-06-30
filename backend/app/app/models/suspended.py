from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from .fact import Fact
from .user import User


class Suspended(Base):
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_suspended = Column(TIMESTAMP(timezone=True), nullable=False)

    suspender = relationship("User", backref=backref("suspensions", cascade="all, delete-orphan"))
    suspended_fact = relationship("Fact", backref=backref("suspensions", cascade="all, delete-orphan"))

    def __init__(self, suspender: User, suspended_fact: Fact, date_suspended: datetime):
        self.suspended_fact = suspended_fact
        self.suspender = suspender
        self.date_suspended = date_suspended
