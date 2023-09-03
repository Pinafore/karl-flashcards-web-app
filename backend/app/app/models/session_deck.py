from typing import TYPE_CHECKING
from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .studyset import StudySet  # noqa: F401
    from .deck import Deck  # noqa: F401
    from .history import History  # noqa: F401


class Session_Deck(Base):
    studyset_id = Column(Integer, ForeignKey("studyset.id"), primary_key=True)
    deck_id = Column(Integer, ForeignKey("deck.id"), primary_key=True)

    studyset = relationship("StudySet", back_populates="session_decks")
    deck = relationship("Deck")

    # def __init__(self, studyset=None, deck=None):
    #     self.studyset = studyset
    #     self.deck = deck
