from typing import TYPE_CHECKING

from app.db.base_class import Base
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

# from .user_deck import user_deck

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .user import User  # noqa: F401
    from .user_deck import User_Deck  # noqa: F401
    from .session import Session  # noqa: F401


class Deck(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    public = Column(Boolean, nullable=False, default=False)

    facts = relationship("Fact", back_populates="deck")
    users = association_proxy('user_decks', 'user')
    user_decks = relationship("User_Deck", back_populates="deck", cascade="all, delete-orphan")
    session = relationship("Session", back_populates="deck")
