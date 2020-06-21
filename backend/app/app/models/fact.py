from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
from app.schemas import Permission
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, ARRAY, cast, Index, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship

from .user import User

if TYPE_CHECKING:
    from .suspended import Suspended  # noqa: F401
    from .deck import Deck  # noqa: F401
    from .history import History  # noqa: F401


def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector('english', exp)


class Fact(Base):
    fact_id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    text = Column(String, index=True, nullable=False)
    answer = Column(String, index=True, nullable=False)
    create_date = Column(TIMESTAMP(timezone=True), nullable=False)
    update_date = Column(TIMESTAMP(timezone=True), nullable=False)
    category = Column(String, index=True)
    identifier = Column(String, index=True)
    answer_lines = Column(ARRAY(String), nullable=False)
    extra = Column(JSONB)

    owner = relationship("User", back_populates="owned_facts")
    deck = relationship("Deck", back_populates="facts")
    history = relationship("History", back_populates="fact")
    suspenders = association_proxy('suspensions', 'suspender')
    markers = association_proxy('marks', 'marker')

    __ts_vector__ = create_tsvector(
        cast(func.coalesce(text, ''), postgresql.TEXT),
        cast(func.coalesce(answer, ''), postgresql.TEXT),
        cast(func.coalesce(category, ''), postgresql.TEXT),
        cast(func.coalesce(identifier, ''), postgresql.TEXT)
    )

    __table_args__ = (
        Index(
            'idx_fact_fts',
            __ts_vector__,
            postgresql_using='gin'
        ),
    )

    @hybrid_method
    def permissions(self, user: User) -> Optional[Permission]:
        if self.user_id == user.id:
            return Permission.owner
        for user_deck in user.user_decks:
            if self.deck == user_deck.deck:
                return user_deck.permissions
        else:
            return None
