from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from app.schemas.suspend_type import SuspendType
from .fact import Fact
from .user import User


class Suspended(Base):
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_suspended = Column(TIMESTAMP(timezone=True), nullable=False)
    suspend_type = Column(Enum(SuspendType), nullable=False)

    suspender = relationship("User", backref=backref("suspensions", cascade="all, delete-orphan"))
    suspended_fact = relationship("Fact", backref=backref("suspensions", cascade="all, delete-orphan"))

    def __init__(self, suspender: User, suspended_fact: Fact, date_suspended: datetime, suspend_type: SuspendType):
        self.suspended_fact = suspended_fact
        self.suspender = suspender
        self.date_suspended = date_suspended
        self.suspend_type = suspend_type
