from sqlalchemy.orm import Session

from app import crud
from app.schemas import DeckCreate
from app.schemas.fact import FactCreate, FactUpdate, FactSearch
from app.tests.utils.fact import create_random_fact_with_deck
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


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

    all_facts = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(deck_ids=[decks[0].id, decks[1].id]))
    assert len(all_facts) == 5
    deck1_facts = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(deck_id=decks[0].id))
    assert len(deck1_facts) == 3
    deck2_facts = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(deck_id=decks[1].id))
    assert len(deck2_facts) == 2
    apple_in_deck1 = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(deck_id=decks[0].id,
                                                                                    text="apple"))
    assert len(apple_in_deck1) == 1
    apple_in_deck2 = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(deck_id=decks[1].id,
                                                                                    text="apple"))
    assert len(apple_in_deck2) == 1
    apple = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(text="apple"))
    assert len(apple) == 2
    identifier = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(identifier="This animal"))
    assert len(identifier) == 3
    category_apple = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(category="apple"))
    assert len(category_apple) == 0
    category_empty_string = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(category=""))
    assert len(category_empty_string) == 5
    category_null = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch())
    assert len(category_null) == 5

    crud.fact.mark(db=db, db_obj=facts[0], user=user)
    chicken = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(marked=True))
    assert len(chicken) == 1

    chicken = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(marked=False))
    assert len(chicken) == 4

    crud.fact.undo_mark(db=db, db_obj=facts[0], user=user)
    chicken = crud.fact.get_eligible_facts(db=db, user=user, filters=FactSearch(marked=True))
    assert len(chicken) == 0