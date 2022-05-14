from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .session import Session  # noqa: F401
from .fact import Fact  # noqa: F401
from .history import History  # noqa: F401


# user_deck = Table("user_deck", Base.metadata,
#                   Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
#                   Column("deck_id", Integer, ForeignKey("deck.id"), primary_key=True)
#                   )
class Session_Fact(Base):
    session_id = Column(Integer, ForeignKey("session.id"), primary_key=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), primary_key=True)
    history_id = Column(Integer, ForeignKey("history.id"))

    session = relationship("Session", back_populates="session_facts")
    fact = relationship("Fact", back_populates="session_facts")
    history = relationship("History", uselist=False)
