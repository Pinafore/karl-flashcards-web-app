from enum import Enum


class Field(str, Enum):
    text = "text"
    answer = "answer"
    deck = "deck"
    identifier = "identifier"
    category = "category"
    extra = "extra"
