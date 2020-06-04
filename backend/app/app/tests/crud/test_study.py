import pytest
from sqlalchemy.orm import Session
from tqdm import tqdm

from app import crud
from app.schemas import FactSearch
from app.schemas.deck import DeckCreate, DeckUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.fact import create_random_fact_with_deck


# noinspection DuplicatedCode
def test_get_eligible_facts(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user = create_random_user(db)
    private_deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user)
    default_deck = crud.deck.get(db=db, id=1)
    user2 = create_random_user(db)
    crud.deck.assign_viewer(db=db, db_obj=private_deck, user=user2)
    user1_facts = []
    user2_facts = []
    user1_facts.append(create_random_fact_with_deck(db, user=user, deck=default_deck))
    user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=default_deck))
    user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=private_deck))

    study_facts = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(deck_id=default_deck.id, studyable=True))
    assert len(study_facts) == 1
    assert study_facts[0] == user1_facts[0]
    assert study_facts[0].user_id == user.id

    study_facts_no_deck = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(studyable=True))
    assert len(study_facts_no_deck) == 1
    assert study_facts_no_deck[0] == user1_facts[0]
    assert study_facts_no_deck[0].user_id == user.id

    study_facts_2 = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(deck_id=default_deck.id, studyable=True))
    assert len(study_facts_2) == 1
    assert study_facts_2[0] == user2_facts[0]
    assert study_facts_2[0].user_id == user2.id

    study_facts_2_no_deck = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(studyable=True))
    assert len(study_facts_2_no_deck) == 2

    last_fact = create_random_fact_with_deck(db, user=user, deck=private_deck)
    user1_facts.append(last_fact)
    study_facts_with_public_fact = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(studyable=True))
    assert len(study_facts_with_public_fact) == 2
    study_facts_with_public_fact_user_2 = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(studyable=True))
    assert len(study_facts_with_public_fact_user_2) == 3

    crud.fact.suspend(db, db_obj=last_fact, user=user)
    study_facts_with_public_fact = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(studyable=True))
    assert len(study_facts_with_public_fact) == 1
    study_facts_with_public_fact_user_2 = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(studyable=True))
    assert len(study_facts_with_public_fact_user_2) == 3

    crud.fact.suspend(db, db_obj=last_fact, user=user2)
    study_facts_with_public_fact = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(studyable=True))
    assert len(study_facts_with_public_fact) == 1
    study_facts_with_public_fact_user_2 = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(studyable=True))
    assert len(study_facts_with_public_fact_user_2) == 2


def test_get_eligible_facts_two_owners(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user1 = create_random_user(db)
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user1)
    user2 = create_random_user(db)
    crud.deck.assign_owner(db=db, db_obj=deck, user=user2)
    user3 = create_random_user(db)
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user3)
    user1_facts = []
    user2_facts = []
    user3_facts = []
    for _ in range(10):
        user1_facts.append(create_random_fact_with_deck(db, user=user1, deck=deck))
        user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=deck))
        user3_facts.append(create_random_fact_with_deck(db, user=user3, deck=deck))
    user1_study = crud.fact.get_eligible_facts(db=db, user=user1, filters=FactSearch(studyable=True))
    user2_study = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(studyable=True))
    user3_study = crud.fact.get_eligible_facts(db=db, user=user3, filters=FactSearch(studyable=True))
    assert len(user1_study) == 20
    assert len(user2_study) == 20
    assert len(user3_study) == 30


def test_get_eligible_facts_stress_test(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user1 = create_random_user(db)
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user1)
    user2 = create_random_user(db)
    crud.deck.assign_owner(db=db, db_obj=deck, user=user2)
    user3 = create_random_user(db)
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user3)
    user1_facts = []
    user2_facts = []
    user3_facts = []
    multiplier = 1
    for _ in tqdm(range(10*multiplier)):
        user1_facts.append(create_random_fact_with_deck(db, user=user1, deck=deck))
        user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=deck))
    for _ in tqdm(range(100 * multiplier)):
        user3_facts.append(create_random_fact_with_deck(db, user=user3, deck=deck))
    user1_study = crud.fact.get_eligible_facts(db=db, user=user1, filters=FactSearch(studyable=True))
    user2_study = crud.fact.get_eligible_facts(db=db, user=user2, filters=FactSearch(studyable=True))
    user3_study = crud.fact.get_eligible_facts(db=db, user=user3, filters=FactSearch(studyable=True))
    assert len(user1_study) == 20*multiplier
    assert len(user2_study) == 20*multiplier
    assert len(user3_study) == 120*multiplier

