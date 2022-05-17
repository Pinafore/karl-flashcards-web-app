from typing import TYPE_CHECKING
from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .studyset import StudySet  # noqa: F401
    from .fact import Fact  # noqa: F401
    from .history import History  # noqa: F401


class Session_Fact(Base):
    studyset_id = Column(Integer, ForeignKey("studyset.id"), primary_key=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), primary_key=True)
    history_id = Column(Integer, ForeignKey("history.id"))

    studyset = relationship("StudySet", back_populates="session_facts")
    fact = relationship("Fact")
    history = relationship("History", uselist=False)
