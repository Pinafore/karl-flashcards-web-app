from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, JSON, ARRAY, Boolean
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.db.base_class import Base


if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .suspended import Suspended  # noqa: F401
    from .deck import Deck  # noqa: F401


class Fact(Base):
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    front = Column(String, index=True, nullable=False)
    back = Column(String, index=True, nullable=False)
    create_date = Column(TIMESTAMP(timezone=True))
    update_date = Column(TIMESTAMP(timezone=True))
    category = Column(String)
    identifier = Column(String)
    answer_lines = Column(ARRAY(String), nullable=False)
    extra = Column(JSON)

    deck = relationship("Deck", back_populates="facts")
    history = relationship("History", back_populates="fact")
    suspenders = association_proxy('suspended', 'suspender')

