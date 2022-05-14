from typing import TYPE_CHECKING, List

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .fact import Fact

if TYPE_CHECKING:
    from .deck import Deck  # noqa: F401
    from .user import User  # noqa: F401
    from .session_fact import Session_Fact  # noqa: F401


class StudySet(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    deck_id = Column(Integer, ForeignKey("deck.id"), index=True)
    is_test = Column(Integer, nullable=False, default=False, index=True)

    deck = relationship("Deck", uselist=False)
    user = relationship("User", uselist=False)
    facts = association_proxy("session_facts", "fact")
    session_facts = relationship("Session_Fact", back_populates="session")

    @property
    def num_facts(self) -> int:
        return len(self.unstudied_facts)

    # https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html
    @hybrid_property
    def completed(self) -> bool:
        return self.num_facts != 0

    @hybrid_property
    def unstudied_facts(self) -> List[Fact]:
        return [session_fact.fact for session_fact in self.session_facts if session_fact.history_id]  # type: ignore
