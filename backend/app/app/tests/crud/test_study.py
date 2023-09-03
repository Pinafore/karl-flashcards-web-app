from sqlalchemy.orm import Session
from tqdm import tqdm

from app import crud
from app.schemas import FactSearch
from app.schemas.deck import DeckCreate
from app.tests.utils.fact import create_random_fact_with_deck
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


# noinspection DuplicatedCode
def test_get_eligible_facts(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user = create_random_user(db)
    private_deck = crud.deck.create_with_owner(db=db, obj_in=deck_in,
                                               user=user)  # owned by user1, user2 is assigned viewer
    default_deck = crud.deck.get(db=db, id=1)
    user2 = create_random_user(db)
    crud.deck.assign_viewer(db=db, db_obj=private_deck, user=user2)
    user1_facts = []
    user2_facts = []
    user1_facts.append(create_random_fact_with_deck(db, user=user, deck=default_deck))  # viewable only to user1
    user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=default_deck))  # viewable only to user1
    user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=private_deck))  # viewable only to user2

    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(deck_id=default_deck.id, studyable=True))
    study_facts = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts) == 1  # Facts seen in default deck by user1
    assert study_facts[0] == user1_facts[0]
    assert study_facts[0].user_id == user.id

    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(studyable=True))
    study_facts_no_deck = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_no_deck) == 1  # Facts viewable by user1 at this point
    assert study_facts_no_deck[0] == user1_facts[0]
    assert study_facts_no_deck[0].user_id == user.id

    query = crud.fact.build_facts_query(db=db, user=user2,
                                        filters=FactSearch(deck_id=default_deck.id, studyable=True))
    study_facts_2 = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_2) == 1  # Facts seen in default deck by user2
    assert study_facts_2[0] == user2_facts[0]
    assert study_facts_2[0].user_id == user2.id

    query = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    study_facts_2_no_deck = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_2_no_deck) == 2  # Facts seen by user2 at this point

    last_fact = create_random_fact_with_deck(db, user=user,
                                             deck=private_deck)  # New fact created in private deck owned by user1, viewable by user2
    user1_facts.append(last_fact)
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(studyable=True))
    study_facts_with_public_fact = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_with_public_fact) == 2  # Facts seen by user1 (one in private deck, one in default)
    query = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    study_facts_with_public_fact_user_2 = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_with_public_fact_user_2) == 3  # Facts seen by user2 (two in private deck, one in default)

    crud.fact.suspend(db, db_obj=last_fact, user=user)  # Fact suspended by owner of fact, still viewable by user2
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(studyable=True))
    study_facts_with_public_fact = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_with_public_fact) == 1  # Facts seen by user1 (only one in public deck)
    query = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    study_facts_with_public_fact_user_2 = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_with_public_fact_user_2) == 3  # Facts seen by user2 (two in private deck, one in default)

    crud.fact.suspend(db, db_obj=last_fact, user=user2)
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(studyable=True))
    study_facts_with_public_fact = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_with_public_fact) == 1  # Facts seen by user1 (only one in public deck)
    query = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    study_facts_with_public_fact_user_2 = crud.fact.get_eligible_facts(query=query)
    assert len(study_facts_with_public_fact_user_2) == 2  # Facts seen by user2 (one in private deck, one in default)


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
    query = crud.fact.build_facts_query(db=db, user=user1, filters=FactSearch(studyable=True))
    query2 = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    query3 = crud.fact.build_facts_query(db=db, user=user3, filters=FactSearch(studyable=True))
    user1_study = crud.fact.get_eligible_facts(query=query)
    user2_study = crud.fact.get_eligible_facts(query=query2)
    user3_study = crud.fact.get_eligible_facts(query=query3)
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
    for _ in tqdm(range(10 * multiplier)):
        user1_facts.append(create_random_fact_with_deck(db, user=user1, deck=deck))
        user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=deck))
    for _ in tqdm(range(100 * multiplier)):
        user3_facts.append(create_random_fact_with_deck(db, user=user3, deck=deck))
    query = crud.fact.build_facts_query(db=db, user=user1, filters=FactSearch(studyable=True))
    query2 = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    query3 = crud.fact.build_facts_query(db=db, user=user3, filters=FactSearch(studyable=True))
    user1_study = crud.fact.get_eligible_facts(query=query)
    user2_study = crud.fact.get_eligible_facts(query=query2)
    user3_study = crud.fact.get_eligible_facts(query=query3)
    assert len(user1_study) == 20 * multiplier
    assert len(user2_study) == 20 * multiplier
    assert len(user3_study) == 120 * multiplier
