from app.db.base_class import Base
from app.schemas.permission import Permission
from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .deck import Deck
from .user import User


# user_deck = Table("user_deck", Base.metadata,
#                   Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
#                   Column("deck_id", Integer, ForeignKey("deck.id"), primary_key=True)
#                   )
class User_Deck(Base):
    deck_id = Column(Integer, ForeignKey("deck.id"), primary_key=True)
    owner_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    permissions = Column(Enum(Permission), nullable=False, default=Permission.viewer)

    user = relationship("User", back_populates="user_decks")
    deck = relationship("Deck", back_populates="user_decks")

    def __init__(self, deck: Deck, user: User, permissions: Permission):
        self.deck = deck
        self.user = user
        self.permissions = permissions
