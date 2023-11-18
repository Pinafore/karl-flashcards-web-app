from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum, TIMESTAMP, SmallInteger
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from pytz import timezone

from app.db.base_class import Base

# from .user_deck import user_deck
from app.schemas import DeckType, Repetition
from app.core.config import settings
from .deck import Deck  # noqa: F401
from .studyset import StudySet
# from app.crud import studyset
from app.db.session import SessionLocal

if TYPE_CHECKING:
    from .suspended import Suspended  # noqa: F401
    from .history import History  # noqa: F401
    from .fact import Fact  # noqa: F401
    from .user_deck import User_Deck  # noqa: F401
    from .test_history import Test_History  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    repetition_model = Column(Enum(Repetition), default=Repetition.karl, nullable=False)
    default_deck_id = Column(Integer, ForeignKey("deck.id"), default=1)
    show_help = Column(Boolean(), default=True, nullable=False)
    dark_mode = Column(Boolean(), default=False, nullable=False)
    pwa_tip = Column(Boolean(), default=False, nullable=False)
    create_date = Column(TIMESTAMP(timezone=True))
    beta_user = Column(Boolean(), default=False, nullable=False)
    recall_target = Column(SmallInteger, default=-1, nullable=False)

    default_deck = relationship("Deck", foreign_keys=default_deck_id)
    owned_facts = relationship("Fact", back_populates="owner")
    history = relationship("History", back_populates="user")
    suspended_facts = association_proxy('suspensions', 'suspended_fact')
    deleted_facts = association_proxy('deletions', 'deleted_fact')
    reported_facts = association_proxy('reporteds', 'reported_fact')
    user_decks = relationship("User_Deck", back_populates="user", cascade="all, delete-orphan")
    all_decks = association_proxy('user_decks', 'deck')
    marked_facts = association_proxy('marks', 'marked_fact')
    test_history = relationship("Test_History", back_populates="user")
    sessions = relationship("StudySet", back_populates="user")

    @hybrid_property
    def decks(self) -> List[Deck]:
        return [deck for deck in self.all_decks if deck.deck_type != DeckType.hidden and deck.deck_type != DeckType.deleted]  # Test if should be schema
        
    @hybrid_property
    def study_set_expiry_date(self) -> Optional[datetime]:
        db = SessionLocal()
        from app.crud import studyset
        study_set = studyset.find_active_study_set(db, self)
        expiry_date = study_set.expiry_date if study_set is not None else None
        db.close()
        return expiry_date
