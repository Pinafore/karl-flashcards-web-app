from typing import TYPE_CHECKING

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .deck import Deck  # noqa: F401
    from .user import User  # noqa: F401
    from .session_fact import Session_Fact  # noqa: F401


class Session(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    deck_id = Column(Integer, ForeignKey("fact.fact_id"), index=True)
    is_test = Column(Integer, nullable=False, default=False, index=True)

    deck = relationship("Deck", uselist=False)
    user = relationship("User", uselist=False)
    facts = association_proxy("session_facts", "fact")
    session_facts = relationship("Session_Fact", back_populates="session")

    @property
    def num_facts(self) -> int:
        return len(self.facts)

    # https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html
    @hybrid_property
    def completed(self) -> bool:
        return self.num_facts != 0
