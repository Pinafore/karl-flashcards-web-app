from typing import TYPE_CHECKING

from sqlalchemy import Table, Column, Integer, ForeignKey

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .deck import Deck  # noqa: F401

user_deck = Table("user_deck", Base.metadata,
                  Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
                  Column("deck_id", Integer, ForeignKey("deck.id"), primary_key=True)
                  )
