from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, ARRAY, cast, Index, func, Boolean
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.schemas import Permission, FactReported
from .user import User

if TYPE_CHECKING:
    from .suspended import Suspended  # noqa: F401
    from .deck import Deck  # noqa: F401
    from .history import History  # noqa: F401
    from .test_history import Test_History  # noqa: F401
    from .studyset import StudySet  # noqa: F401
from .session_fact import Session_Fact  # noqa: F401


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
    deleters = association_proxy('deletions', 'deleter')
    reporters = association_proxy('reporteds', 'reporter')
    markers = association_proxy('marks', 'marker')
    test_history = relationship("Test_History", back_populates="fact")
    studysets = association_proxy('session_facts', 'studyset', creator=lambda studyset: Session_Fact(studyset=studyset))

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
        for user_deck in user.user_decks:  # type: ignore # association proxy object is actually iterable
            if self.deck == user_deck.deck:
                return user_deck.permissions
        else:
            return None

    @hybrid_method
    def find_reports(self, user: User) -> List[FactReported]:
        if user.is_superuser:
            return [FactReported.construct(report_id=ind, reporter_id=report.user_id,
                                           reporter_username=report.reporter.username, **report.suggestion)
                    for ind, report in enumerate(self.reporteds)]  # type: ignore # reporteds is user end
        else:
            return [FactReported.construct(report_id=ind, reporter_id=report.user_id,
                                           reporter_username=report.reporter.username, **report.suggestion)
                    for ind, report in enumerate(self.reporteds) if report.user_id == user.id]  # type: ignore

    @hybrid_method
    def is_marked(self, user: User) -> bool:
        return True if user in self.markers else False

    @hybrid_method
    def is_suspended(self, user: User) -> bool:
        return True if user in self.suspenders else False

    @hybrid_method
    def is_deleted(self, user: User) -> bool:
        return True if user in self.deleters else False

    @hybrid_method
    def is_reported(self, user: User) -> bool:
        return True if user in self.reporters else False

    @hybrid_property
    def deck_name(self) -> str:
        return self.deck.title
