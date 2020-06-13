from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.schemas import Permission
from .user import User

if TYPE_CHECKING:
    from .suspended import Suspended  # noqa: F401
    from .deck import Deck  # noqa: F401
    from .history import History  # noqa: F401


class Fact(Base):
    fact_id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    text = Column(String, index=True, nullable=False)
    answer = Column(String, index=True, nullable=False)
    create_date = Column(TIMESTAMP(timezone=True), nullable=False)
    update_date = Column(TIMESTAMP(timezone=True), nullable=False)
    category = Column(String)
    identifier = Column(String)
    answer_lines = Column(ARRAY(String), nullable=False)
    extra = Column(JSONB)

    owner = relationship("User", back_populates="owned_facts")
    deck = relationship("Deck", back_populates="facts")
    history = relationship("History", back_populates="fact")
    suspenders = association_proxy('suspensions', 'suspender')
    markers = association_proxy('marks', 'marker')

    @hybrid_method
    def permissions(self, user: User) -> Optional[Permission]:
        if self.user_id == user.id:
            return Permission.owner
        for user_deck in user.user_decks:
            if self.deck == user_deck.deck:
                return user_deck.permissions
        else:
            return None
