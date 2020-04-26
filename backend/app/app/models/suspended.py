from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.schemas.suspend_type import SuspendType

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .user import User  # noqa: F401


class Suspended(Base):
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("fact.card_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_suspended = Column(TIMESTAMP(timezone=True), nullable=False)
    type = Column(Enum(SuspendType), nullable=False)

    suspender = relationship("User", backref="suspensions", cascade="all")
    suspended_fact = relationship("Fact", backref="suspensions", cascade="all")
