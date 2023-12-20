from typing import TYPE_CHECKING

from app.db.base_class import Base
from app.schemas.log import Log
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Enum, Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .fact import Fact  # noqa: F401
    from .user import User  # noqa: F401


class Test_History(Base):
    id = Column(Integer, primary_key=True, index=True)
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    fact_id = Column(Integer, ForeignKey("fact.fact_id"))
    response = Column(Boolean(), nullable=False, index=True)
    details = Column(JSONB)

    fact = relationship("Fact", back_populates="test_history")
    user = relationship("User", back_populates="test_history")
