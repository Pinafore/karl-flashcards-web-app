from app import crud, models
from app.schemas.fact import FactCreate
from app.tests.utils.deck import create_random_deck
from app.tests.utils.utils import random_lower_string
from sqlalchemy.orm import Session


def create_random_fact(db: Session, user: models.User) -> models.Fact:
    text = random_lower_string()
    identifier = random_lower_string()
    answer = random_lower_string()
    deck = create_random_deck(db=db, user=user)
    deck_id = deck.id
    answer_lines = [answer]
    extra = {"type": "Noodles"}

    fact_in = FactCreate(text=text,
                         answer=answer,
                         deck_id=deck_id,
                         answer_lines=answer_lines,
                         identifier=identifier,
                         extra=extra)
    return crud.fact.create_with_owner(db=db, obj_in=fact_in, user=user)


def create_random_fact_with_deck(db: Session, user: models.User, deck: models.Deck) -> models.Fact:
    text = random_lower_string()
    identifier = random_lower_string()
    answer = random_lower_string()
    deck_id = deck.id
    answer_lines = [answer]
    extra = {"type": "Noodles"}

    fact_in = FactCreate(text=text,
                         answer=answer,
                         deck_id=deck_id,
                         answer_lines=answer_lines,
                         identifier=identifier,
                         extra=extra)
    return crud.fact.create_with_owner(db=db, obj_in=fact_in, user=user)
