from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.schemas.log import Log

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .user import User  # noqa: F401


class History(Base):
    id = Column(Integer, primary_key=True, index=True)
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"), nullable=False)
    log_type = Column(Enum(Log), nullable=False)
    details = Column(JSONB)
    # repetition_model = Column(Enum(Repetition), default=Repetition.leitner, nullable=False)
    # typed = Column(String, nullable=False)
    # response = Column(String, nullable=False)
    # front_seconds_elapsed = Column(Integer, nullable=False)
    # back_seconds_elapsed = Column(Integer, nullable=False)
    # latest_study = Column(Boolean)

    fact = relationship("Fact", back_populates="history")
    user = relationship("User", back_populates="history")
