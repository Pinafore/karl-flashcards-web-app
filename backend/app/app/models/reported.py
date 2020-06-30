from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from app.schemas import FactToReport
from .fact import Fact
from .user import User


class Reported(Base):
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_reported = Column(TIMESTAMP(timezone=True), nullable=False)
    suggestion = Column(JSONB)

    reporter = relationship("User", backref=backref("reporteds", cascade="all, delete-orphan"))
    reported_fact = relationship("Fact", backref=backref("reporteds", cascade="all, delete-orphan"))

    def __init__(self, reporter: User, reported_fact: Fact, date_reported: datetime,
                 suggestion: FactToReport):
        self.reported_fact = reported_fact
        self.reporter = reporter
        self.date_reported = date_reported
        self.suggestion = suggestion.dict()
