from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, ARRAY, cast, Index, func, Boolean
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.schemas import Permission
from .user import User

if TYPE_CHECKING:
    from .fact import Fact

class Mnemonic(Base):
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studyset.id"))
    fact_id = Column(Integer, ForeignKey("fact.fact_id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    user_rating = Column(Integer, nullable=True)
    
    is_offensive = Column(Boolean, nullable=True)
    is_incorrect_definition = Column(Boolean, nullable=True)
    is_difficult_to_understand = Column(Boolean, nullable=True)
    is_bad_keyword_link = Column(Boolean, nullable=True)
    is_bad_for_other_reason = Column(Boolean, nullable=True)
    other_reason_text = Column(String, nullable=True)

    correct = Column(Boolean(), index=True)
    
    create_date = Column(TIMESTAMP(timezone=True), nullable=True)

