from typing import List

from app.schemas import Field, Deck
from pydantic import BaseModel


class FileProps(BaseModel):
    headers: List[Field] = [Field.text, Field.answer]
    default_deck: Deck
    delimeter: str = "\t"
