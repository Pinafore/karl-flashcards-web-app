from typing import TYPE_CHECKING, List

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app import schemas

if TYPE_CHECKING:
    from .deck import Deck  # noqa: F401
    from .user import User  # noqa: F401
    from .fact import Fact
from .session_fact import Session_Fact  # noqa: F401
from .session_deck import Session_Deck  # noqa: F401


class StudySet(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    is_test = Column(Boolean, nullable=False, default=False, index=True)

    decks = association_proxy("session_decks", "deck", creator=lambda deck: Session_Deck(deck=deck))
    session_decks = relationship("Session_Deck", back_populates="studyset")
    user = relationship("User", uselist=False)
    facts = association_proxy("session_facts", "fact", creator=lambda fact: Session_Fact(fact=fact))
    session_facts = relationship("Session_Fact", back_populates="studyset")

    @property
    def num_unstudied(self) -> int:
        return len(self.unstudied_facts)

    # https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html
    @hybrid_property
    def completed(self) -> bool:
        return self.num_unstudied != 0

    @hybrid_property
    def unstudied_facts(self) -> List[schemas.Fact]:
        return [schemas.Fact.from_orm(session_fact.fact) for session_fact in self.session_facts if  # type: ignore
                not session_fact.history_id]  # type: ignore

    @hybrid_property
    def all_facts(self) -> List[schemas.Fact]:
        return [schemas.Fact.from_orm(fact) for fact in self.facts]  # type: ignore

    @hybrid_property
    def all_decks(self) -> List[schemas.Deck]:
        return [schemas.Deck.from_orm(deck) for deck in self.decks]  # type: ignore
