from sqlalchemy.orm import Session
from tqdm import tqdm

from app import crud
from app.schemas import DeckCreate
from app.schemas.fact import FactCreate, FactSearch, FactToReport
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


def test_suspend_many_facts(db: Session) -> None:
    title = random_lower_string()
    deck_in = DeckCreate(title=title)
    user1 = create_random_user(db)
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=user1)
    user2 = create_random_user(db)
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user2)
    user1_facts = []
    user2_facts = []
    multiplier = 100
    for _ in tqdm(range(10 * multiplier)):
        user1_facts.append(create_random_fact_with_deck(db, user=user1, deck=deck))
        user2_facts.append(create_random_fact_with_deck(db, user=user2, deck=deck))
    query = crud.fact.build_facts_query(db=db, user=user1, filters=FactSearch(studyable=True))
    query2 = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    user1_study = crud.fact.get_eligible_facts(query=query)
    user2_study = crud.fact.get_eligible_facts(query=query2)
    assert len(user1_study) == 10 * multiplier
    assert len(user2_study) == 20 * multiplier

    for number in tqdm(range(5 * multiplier)):
        crud.fact.suspend(db, db_obj=user1_facts[number], user=user1)
        crud.fact.report(db, db_obj=user1_facts[number], user=user2, suggestion=FactToReport(comment="report"))
        crud.fact.remove(db, db_obj=user2_facts[number], user=user2)

    query = crud.fact.build_facts_query(db=db, user=user1, filters=FactSearch(studyable=True))
    query2 = crud.fact.build_facts_query(db=db, user=user2, filters=FactSearch(studyable=True))
    user1_study = crud.fact.get_eligible_facts(query=query)
    user2_study = crud.fact.get_eligible_facts(query=query2)
    assert len(user1_study) == 5 * multiplier
    assert len(user2_study) == 10 * multiplier
