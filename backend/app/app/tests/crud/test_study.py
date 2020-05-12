from sqlalchemy.orm import Session

from app import crud
from app.schemas.deck import DeckCreate, DeckUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.fact import create_random_fact_with_deck

def test_get_eligible_facts(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user = create_random_user(db)
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user)
    default_deck = crud.deck.get(db=db, id=1)
    lit_deck = crud.deck.get(db=db, id=2)
    lit = crud.deck.assign_viewer(db=db, db_obj=lit_deck, user=user)
    user2 = create_random_user(db)
    user1_facts = []
    user2_facts = []
    for _ in range(1):
        user1_facts.append(create_random_fact_with_deck(db, user=user, deck=default_deck))
    for _ in range(1):
        user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=default_deck))
    study_facts = crud.fact.get_eligible_facts(db=db, user=user, deck_ids=[1])
    assert len(study_facts) == 1
    assert study_facts[0] == user1_facts[0]
