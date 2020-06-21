from app import crud
from app.schemas import DeckCreate
from app.schemas.fact import FactCreate, FactSearch
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from sqlalchemy.orm import Session


def test_search_facts(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    title2 = random_lower_string()
    deck_in2 = DeckCreate(title=title2)
    user = create_random_user(db)
    decks = []
    decks.append(crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user))
    decks.append(crud.deck.create_with_owner(db=db, obj_in=deck_in2, user=user))
    facts = []
    facts.append(crud.fact.create_with_owner(db=db,
                                             obj_in=FactCreate(text="chicken",
                                                               answer="noodles",
                                                               deck_id=decks[0].id,
                                                               answer_lines=["noodles"],
                                                               identifier="This object",
                                                               extra={"type": "testing"}), user=user))
    facts.append(crud.fact.create_with_owner(db=db,
                                             obj_in=FactCreate(text="chicken",
                                                               answer="appleseed",
                                                               deck_id=decks[0].id,
                                                               answer_lines=["appleseed"],
                                                               identifier="This animal",
                                                               extra={"type": "testing"}), user=user))
    facts.append(crud.fact.create_with_owner(db=db,
                                             obj_in=FactCreate(text="chicken",
                                                               answer="noodles",
                                                               deck_id=decks[1].id,
                                                               answer_lines=["noodles"],
                                                               identifier="This object",
                                                               extra={"type": "testing"}), user=user))
    facts.append(crud.fact.create_with_owner(db=db,
                                             obj_in=FactCreate(text="apple",
                                                               answer="appleseed",
                                                               deck_id=decks[0].id,
                                                               answer_lines=["noodles"],
                                                               identifier="This animal",
                                                               extra={"type": "testing"}), user=user))
    facts.append(crud.fact.create_with_owner(db=db,
                                             obj_in=FactCreate(text="apple",
                                                               answer="appleseed",
                                                               deck_id=decks[1].id,
                                                               answer_lines=["noodles"],
                                                               identifier="This animal",
                                                               extra={"type": "testing"}), user=user))

    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(deck_ids=[decks[0].id, decks[1].id]))
    all_facts = crud.fact.get_eligible_facts(query=query)
    assert len(all_facts) == 5
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(deck_id=decks[0].id))
    deck1_facts = crud.fact.get_eligible_facts(query=query)
    assert len(deck1_facts) == 3
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(deck_id=decks[1].id))
    deck2_facts = crud.fact.get_eligible_facts(query=query)
    assert len(deck2_facts) == 2
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(deck_id=decks[0].id,
                                                                                       text="apple"))
    apple_in_deck1 = crud.fact.get_eligible_facts(query=query)
    assert len(apple_in_deck1) == 1
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(deck_id=decks[1].id,
                                                                                       text="apple"))
    apple_in_deck2 = crud.fact.get_eligible_facts(query=query)
    assert len(apple_in_deck2) == 1
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(text="apple"))
    apple = crud.fact.get_eligible_facts(query=query)
    assert len(apple) == 2
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(identifier="This animal"))
    identifier = crud.fact.get_eligible_facts(query=query)
    assert len(identifier) == 3
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(category="apple"))
    category_apple = crud.fact.get_eligible_facts(query=query)
    assert len(category_apple) == 0
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(category=""))
    category_empty_string = crud.fact.get_eligible_facts(query=query)
    assert len(category_empty_string) == 5
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch())
    category_null = crud.fact.get_eligible_facts(query=query)
    assert len(category_null) == 5

    crud.fact.mark(db=db, db_obj=facts[0], user=user)
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(marked=True))
    chicken = crud.fact.get_eligible_facts(query=query)
    assert len(chicken) == 1

    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(marked=False))
    chicken = crud.fact.get_eligible_facts(query=query)
    assert len(chicken) == 4

    crud.fact.undo_mark(db=db, db_obj=facts[0], user=user)
    query = crud.fact.build_facts_query(db=db, user=user, filters=FactSearch(marked=True))
    chicken = crud.fact.get_eligible_facts(query=query)
    assert len(chicken) == 0
