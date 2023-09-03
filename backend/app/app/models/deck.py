from typing import TYPE_CHECKING

from app.db.base_class import Base
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.schemas import DeckType

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .user import User  # noqa: F401
    from .user_deck import User_Deck  # noqa: F401
    from .studyset import StudySet  # noqa: F401
from .session_deck import Session_Deck  # noqa: F401


class Deck(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    deck_type = Column(Enum(DeckType), nullable=False, default=DeckType.default, index=True)

    facts = relationship("Fact", back_populates="deck")
    users = association_proxy("user_decks", "user")
    user_decks = relationship("User_Deck", back_populates="deck", cascade="all, delete-orphan")
    studysets = association_proxy("session_deck", "studyset", creator=lambda studyset: Session_Deck(studyset=studyset))
