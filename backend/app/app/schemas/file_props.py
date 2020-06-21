from typing import Optional, List

from pydantic import BaseModel


from app.schemas import Field, Deck


class FileProps(BaseModel):
    headers: List[Field] = [Field.text, Field.answer]
    default_deck: Deck
    delimeter: str = "\t"


