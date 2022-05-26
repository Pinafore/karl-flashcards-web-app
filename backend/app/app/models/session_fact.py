from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
from app.db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.schemas import Permission, FactReported
from . import Deck

if TYPE_CHECKING:
    from .studyset import StudySet  # noqa: F401
    from .fact import Fact  # noqa: F401
    from .history import History  # noqa: F401


# noinspection PyCallingNonCallable
class Session_Fact(Base):
    studyset_id = Column(Integer, ForeignKey("studyset.id"), primary_key=True)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), primary_key=True)
    history_id = Column(Integer, ForeignKey("history.id"))
    rationale = Column(String)

    studyset = relationship("StudySet", back_populates="session_facts")
    fact = relationship("Fact")
    history = relationship("History", uselist=False)

    @hybrid_property
    def completed(self) -> bool:
        return self.history.correct if self.history and self.history.correct else False

    @hybrid_property
    def permission(self) -> Optional[Permission]:
        return self.fact.permissions(user=self.studyset.user)

    @hybrid_property
    def reports(self) -> List[FactReported]:
        return self.fact.find_reports(user=self.studyset.user)

    @hybrid_property
    def marked(self) -> bool:
        return self.fact.is_marked(user=self.studyset.user)

    @hybrid_property
    def suspended(self) -> bool:
        return self.fact.is_suspended(user=self.studyset.user)

    @hybrid_property
    def deleted(self) -> bool:
        return self.fact.is_deleted(user=self.studyset.user)

    @hybrid_property
    def reported(self) -> bool:
        return bool(self.reports)

    @hybrid_property
    def deck_id(self) -> int:
        return self.fact.deck_id

    @hybrid_property
    def user_id(self) -> int:
        return self.fact.user_id

    @hybrid_property
    def text(self) -> str:
        return self.fact.text

    @hybrid_property
    def answer(self) -> str:
        return self.fact.answer

    @hybrid_property
    def create_date(self) -> datetime:
        return self.fact.create_date

    @hybrid_property
    def update_date(self) -> datetime:
        return self.fact.update_date

    @hybrid_property
    def category(self) -> Optional[str]:
        return self.fact.category

    @hybrid_property
    def identifier(self) -> Optional[str]:
        return self.fact.identifier

    @hybrid_property
    def answer_lines(self) -> List[str]:
        return self.fact.answer_lines

    @hybrid_property
    def deck(self) -> Deck:
        return self.fact.deck
