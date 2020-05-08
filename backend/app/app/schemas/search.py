from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Json


# Shared properties
from app.schemas.deck import Deck


class Search(BaseModel):
    text: Optional[str] = None
    deck_ids: Optional[List[int]] = None
