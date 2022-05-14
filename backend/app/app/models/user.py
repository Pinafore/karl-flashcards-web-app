from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum, TIMESTAMP, SmallInteger
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.schemas.repetition import Repetition

# from .user_deck import user_deck

if TYPE_CHECKING:
    from .suspended import Suspended  # noqa: F401
    from .history import History  # noqa: F401
    from .deck import Deck  # noqa: F401
    from .fact import Fact  # noqa: F401
    from .user_deck import User_Deck  # noqa: F401
    from .test_history import Test_History  # noqa: F401
    from .session import Session  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    repetition_model = Column(Enum(Repetition), default=Repetition.leitner, nullable=False)
    default_deck_id = Column(Integer, ForeignKey("deck.id"), default=1)
    show_help = Column(Boolean(), default=True, nullable=False)
    dark_mode = Column(Boolean(), default=False, nullable=False)
    pwa_tip = Column(Boolean(), default=False, nullable=False)
    create_date = Column(TIMESTAMP(timezone=True))
    beta_user = Column(Boolean(), default=False, nullable=False)
    recall_target = Column(SmallInteger, default=-1, nullable=False)
    next_test_mode = Column(SmallInteger, default=0, nullable=False)
    last_test_date = Column(TIMESTAMP(timezone=True), nullable=True)

    default_deck = relationship("Deck", foreign_keys=default_deck_id)
    owned_facts = relationship("Fact", back_populates="owner")
    history = relationship("History", back_populates="user")
    suspended_facts = association_proxy('suspensions', 'suspended_fact')
    deleted_facts = association_proxy('deletions', 'deleted_fact')
    reported_facts = association_proxy('reporteds', 'reported_fact')
    user_decks = relationship("User_Deck", back_populates="user", cascade="all, delete-orphan")
    decks = association_proxy('user_decks', 'deck')
    marked_facts = association_proxy('marks', 'marked_fact')
    test_history = relationship("Test_History", back_populates="user")
    sessions = relationship("Session", back_populates="user")
