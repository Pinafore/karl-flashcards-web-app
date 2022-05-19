from app import crud
from app.schemas.deck import DeckCreate
from app.tests.utils.fact import create_random_fact_with_deck
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from app.schemas.fact import FactCreate, FactSearch
from sqlalchemy.orm import Session


def test_get_multi_by_owner(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user = create_random_user(db)
    decks1 = crud.deck.get_multi_by_owner(db, user=user, skip=1, limit=1)
    decks2 = crud.deck.get_multi_by_owner(db, user=user, skip=None, limit=1)
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user)
    decks3 = crud.deck.get_multi_by_owner(db, user=user, skip=1)
    decks4 = crud.deck.get_multi_by_owner(db, user=user)
    assert decks1 == []
    assert decks2[0].id == 1
    assert decks3 != []
    assert decks3[0] is deck
    assert len(decks4) == 2


def test_find_or_create(db: Session) -> None:
    user = create_random_user(db)
    assert len(user.decks) == 1
    deck = crud.deck.find_or_create(db, proposed_deck="Noodles", user=user)
    assert len(user.decks) == 2
    assert user in deck.users
    deck2 = crud.deck.find_or_create(db, proposed_deck="Noodles", user=user)
    assert len(user.decks) == 2
    deck3 = crud.deck.find_or_create(db, proposed_deck="sdfasdf", user=user)
    assert len(user.decks) == 3


def test_delete_deck(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user = create_random_user(db)
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user)
    create_random_fact_with_deck(db, user=user, deck=deck)
    create_random_fact_with_deck(db, user=user, deck=deck)
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch())
    all_facts = crud.fact.get_eligible_facts(query=query)
    assert len(all_facts) == 2
    crud.deck.remove_for_user(db=db, db_obj=deck, user=user)
    all_facts = crud.fact.get_eligible_facts(query=query)
    assert len(all_facts) == 0
# def test_get_deck(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     deck_in = DeckCreate(title=title, description=description)
#     user = create_random_user(db)
#     deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, owner_id=user.id)
#     stored_deck = crud.deck.get(db=db, id=deck.fact_id)
#     assert stored_deck
#     assert deck.fact_id == stored_deck.fact_id
#     assert deck.title == stored_deck.title
#     assert deck.description == stored_deck.description
#     assert deck.owner_id == stored_deck.owner_id
#
#
# def test_update_deck(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     deck_in = DeckCreate(title=title, description=description)
#     user = create_random_user(db)
#     deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, owner_id=user.id)
#     description2 = random_lower_string()
#     deck_update = DeckUpdate(description=description2)
#     deck2 = crud.deck.update(db=db, db_obj=deck, obj_in=deck_update)
#     assert deck.fact_id == deck2.id
#     assert deck.title == deck2.title
#     assert deck2.description == description2
#     assert deck.owner_id == deck2.owner_id
#
#
# def test_delete_deck(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     deck_in = DeckCreate(title=title, description=description)
#     user = create_random_user(db)
#     deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, owner_id=user.id)
#     deck2 = crud.deck.remove(db=db, id=deck.fact_id)
#     deck3 = crud.deck.get(db=db, id=deck.fact_id)
#     assert deck3 is None
#     assert deck2.id == deck.fact_id
#     assert deck2.title == title
#     assert deck2.description == description
#     assert deck2.owner_id == user.id
