from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.deck import DeckCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_deck(db: Session, user: models.User) -> models.Deck:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    return crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user)
