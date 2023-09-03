from datetime import datetime

from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from .fact import Fact
from .user import User


class Marked(Base):
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_marked = Column(TIMESTAMP(timezone=True), nullable=False)

    marker = relationship("User", backref=backref("marks", cascade="all, delete-orphan"))
    marked_fact = relationship("Fact", backref=backref("marks", cascade="all, delete-orphan"))

    def __init__(self, marker: User, marked_fact: Fact, date_marked: datetime):
        self.marked_fact = marked_fact
        self.marker = marker
        self.date_marked = date_marked
