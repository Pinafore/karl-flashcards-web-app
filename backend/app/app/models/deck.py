from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .user_deck import user_deck

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .user import User  # noqa: F401


class Deck(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    public = Column(Boolean, nullable=False, default=False)

    facts = relationship("Fact", back_populates="deck")
    users = relationship("User", secondary=user_deck, back_populates="decks")
