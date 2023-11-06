from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base_class import Base
from sqlalchemy import Column, Integer, Enum, ForeignKey, Boolean, TIMESTAMP, String, func
from sqlalchemy.orm import relationship
from pytz import timezone

from app.schemas import Repetition, SetType
from app.core.config import settings

if TYPE_CHECKING:  # noqa: F401
    from .user import User  # noqa: F401
from .deck import Deck
from .session_fact import Session_Fact  # noqa: F401
from .session_deck import Session_Deck  # noqa: F401

from app.utils.utils import logger, log_time, time_it
class StudySet(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    create_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    set_type = Column(Enum(SetType), nullable=False, server_default=SetType.normal, index=True)
    repetition_model = Column(Enum(Repetition), nullable=False, server_default=Repetition.karl)
    debug_id = Column(String)
    retired = Column(Boolean)

    decks = association_proxy("session_decks", "deck", creator=lambda deck: Session_Deck(deck=deck))
    session_decks = relationship("Session_Deck", back_populates="studyset")
    user = relationship("User", uselist=False)
    facts = association_proxy("session_facts", "fact", creator=lambda fact: Session_Fact(fact=fact))
    session_facts = relationship("Session_Fact", back_populates="studyset")

    @property
    def num_decks(self) -> int:
        return len(self.decks)

    @property
    def num_facts(self) -> int:
        return len(self.facts)

    @property
    def num_unstudied(self) -> int:
        return len(self.unstudied_facts)
    
    # https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html
    @hybrid_property
    def is_test(self) -> bool:
        return self.set_type == SetType.test
    
    @hybrid_property
    def is_normal(self) -> bool:
        return self.set_type == SetType.normal

    @hybrid_property
    def is_post_test(self) -> bool:
        return self.set_type == SetType.post_test
    
    @hybrid_property
    def completed(self) -> bool:
        logger.info(f"Num completed {self.num_unstudied}")
        return self.num_unstudied == 0 or self.retired is True  # Retired checks if deck was deleted!

    # Modify to include facts to study again?
    # TODO: Optimize
    @hybrid_property
    def unstudied_facts(self) -> List[Session_Fact]:
        unstudied_facts = [session_fact for session_fact in self.session_facts if  # type: ignore
                not (
                        session_fact.completed or session_fact.suspended or session_fact.reported or session_fact.deleted)]
        logger.info(f"Unstudied facts {unstudied_facts}")
        return unstudied_facts

    # maybe change to return session_fact
    # Some reason list comprehension is necessary for pydantic to see models
    @hybrid_property
    def all_facts(self) -> List[Session_Fact]:
        return [session_fact for session_fact in self.session_facts if  # type: ignore
                not (session_fact.suspended or session_fact.reported or session_fact.deleted)]

    @hybrid_property
    def all_decks(self) -> List[Deck]:
        return [deck for deck in self.decks]  # type: ignore

    @hybrid_property
    def is_first_pass(self) -> bool:
        for fact in self.unstudied_facts:
            if fact.history_id is None:
                return True
        return False

    @hybrid_property
    def short_description(self) -> str:
        num_decks = len(self.decks)
        return_str = "" if self.is_first_pass else "Re-"
        if len(self.user.decks) == num_decks or num_decks == 0:
            return_str += f"Learn: All"
        elif num_decks > 1:
            return_str += f"Learn: {num_decks} Decks"
        else:
            return_str += f"Learn: {self.decks[0].title}"
        return return_str

    @hybrid_property
    def expanded_description(self) -> str:
        num_decks = len(self.decks)
        num_facts = len(self.unstudied_facts)
        num_unstudied = len(self.unstudied_facts)
        if len(self.user.decks) == num_decks or num_decks == 0:
            return_str = f"Decks: All"
        else:
            return_str = f"Decks: {', '.join(deck.title for deck in self.decks)}"
        return_str += f"\nFacts: {num_facts} Total, {num_unstudied} Remaining\nFirst Pass:{self.is_first_pass}"
        return return_str

    @hybrid_property
    def not_started(self) -> bool:
        return self.num_unstudied == self.num_facts

    @hybrid_property
    def expired(self) -> bool:
        return not self.is_post_test and datetime.now(timezone('UTC')) > self.expiry_date
    
    @hybrid_property
    def expiry_date(self) -> datetime:
        return None if self.is_post_test else self.create_date + timedelta(hours=settings.STUDY_SET_EXPIRATION_HOURS)
