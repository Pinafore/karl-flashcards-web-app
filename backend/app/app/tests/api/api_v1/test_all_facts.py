import json
from typing import Dict, Tuple

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import User
from app.schemas import FactToReport
from app.tests.utils.deck import create_random_deck
from app.tests.utils.fact import create_random_fact, create_random_fact_with_deck
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    data_string = """
  {
    "text": "He also took photos of his cross-dressing friend Marcel Duchamp as the Rrose Selavy",
    "answer": "Man Ray [accept Emmanuel Radnitzky]",
    "deck_id": "1",
    "answer_lines": [
      "Man Ray [accept Emmanuel Radnitzky]",
      "{Man Ray} (accept {Emmanuel Radnitzky} early)",
      "Man {Ray} (Emmanuel Radnitzky)",
      "Man Ray [or Emmanuel Radnitzky]",
      "Man_Ray"
    ],
    "identifier": "this entity",
    "category": "Art",
    "extra": {
      "type": "quizbowl",
      "tournament": "ACF Winter",
      "difficulty": "College",
      "dataset": "protobowl",
      "proto_id": "5476990eea23cca905506d91",
      "qdb_id": null,
      "clue_type": "tokenized_clue",
      "sentence": 4,
      "wiki_page": "Man_Ray"
    }
  }
    """
    data = json.loads(data_string)
    response = client.post(
        f"{settings.API_V1_STR}/facts/", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    assert content["text"] == data["text"]
    assert content["extra"] == data["extra"]


def test_read_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    fact = create_random_fact(db, normal_user_token_headers[1])
    response = client.get(
        f"{settings.API_V1_STR}/facts/{fact.fact_id}", headers=normal_user_token_headers[0],
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    assert content["fact_id"] == fact.fact_id


def test_read_facts(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/facts/?limit=5", headers=normal_user_token_headers[0],
    )
    assert_success(response)


def test_update_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    fact = create_random_fact(db, normal_user_token_headers[1])
    old_text = fact.text
    new_text = random_lower_string()
    data = {"text": new_text}
    response = client.put(
        f"{settings.API_V1_STR}/facts/{fact.fact_id}", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    db.refresh(fact)
    assert old_text != content["text"]
    assert new_text == content["text"]
    assert content["text"] == fact.text


def test_update_unowned_fact_when_deck_viewer(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    other_user = create_random_user(db)
    deck = create_random_deck(db, user=other_user)
    fact = create_random_fact_with_deck(db=db, user=other_user, deck=deck)
    user = normal_user_token_headers[1]
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user)
    assert user is not fact.owner
    new_text = random_lower_string()
    data = {"text": new_text}
    response = client.put(
        f"{settings.API_V1_STR}/facts/{fact.fact_id}", headers=normal_user_token_headers[0], json=data,
    )
    assert response.status_code == 401


def test_update_unowned_fact_when_deck_owner(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    other_user = create_random_user(db)
    deck = create_random_deck(db, user=other_user)
    fact = create_random_fact_with_deck(db=db, user=other_user, deck=deck)
    user = normal_user_token_headers[1]
    crud.deck.assign_owner(db=db, db_obj=deck, user=user)
    assert user is not fact.owner
    old_text = fact.text
    new_text = random_lower_string()
    data = {"text": new_text}
    response = client.put(
        f"{settings.API_V1_STR}/facts/{fact.fact_id}", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    db.refresh(fact)
    assert old_text != content["text"]
    assert new_text == content["text"]
    assert content["text"] == fact.text


def test_delete_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    fact = create_random_fact(db, normal_user_token_headers[1])
    user = normal_user_token_headers[1]
    assert user is fact.owner
    response = client.delete(
        f"{settings.API_V1_STR}/facts/{fact.fact_id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.deleters


def test_delete_unowned_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    other_user = create_random_user(db)
    deck = create_random_deck(db, user=other_user)
    fact = create_random_fact_with_deck(db=db, user=other_user, deck=deck)
    user = normal_user_token_headers[1]
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user)
    assert user is not fact.owner
    response = client.delete(
        f"{settings.API_V1_STR}/facts/{fact.fact_id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.deleters


def test_suspend_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    fact = create_random_fact(db, normal_user_token_headers[1])
    user = normal_user_token_headers[1]
    assert user is fact.owner
    response = client.put(
        f"{settings.API_V1_STR}/facts/suspend/{fact.fact_id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.suspenders


def test_suspend_unowned_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    other_user = create_random_user(db)
    deck = create_random_deck(db, user=other_user)
    fact = create_random_fact_with_deck(db=db, user=other_user, deck=deck)
    user = normal_user_token_headers[1]
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user)
    assert user is not fact.owner
    response = client.put(
        f"{settings.API_V1_STR}/facts/suspend/{fact.fact_id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.suspenders


def test_report_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    fact = create_random_fact(db, normal_user_token_headers[1])
    user = normal_user_token_headers[1]
    assert user is fact.owner
    suggestion = FactToReport(text="CHICKEN", answer="NOODLES", comment="THIS IS A REPORT").dict()
    response = client.put(
        f"{settings.API_V1_STR}/facts/report/{fact.fact_id}", headers=normal_user_token_headers[0], json=suggestion,
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.reporters


def test_report_unowned_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    other_user = create_random_user(db)
    deck = create_random_deck(db, user=other_user)
    fact = create_random_fact_with_deck(db=db, user=other_user, deck=deck)
    user = normal_user_token_headers[1]
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user)
    assert user is not fact.owner
    suggestion = FactToReport(text="CHICKEN", answer="NOODLES", comment="THIS IS A REPORT").dict()
    response = client.put(
        f"{settings.API_V1_STR}/facts/report/{fact.fact_id}", headers=normal_user_token_headers[0], json=suggestion
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.reporters


def test_mark_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    fact = create_random_fact(db, normal_user_token_headers[1])
    user = normal_user_token_headers[1]
    assert user is fact.owner
    response = client.put(
        f"{settings.API_V1_STR}/facts/mark/{fact.fact_id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.markers


def test_mark_unowned_fact(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    other_user = create_random_user(db)
    deck = create_random_deck(db, user=other_user)
    fact = create_random_fact_with_deck(db=db, user=other_user, deck=deck)
    user = normal_user_token_headers[1]
    crud.deck.assign_viewer(db=db, db_obj=deck, user=user)
    assert user is not fact.owner
    response = client.put(
        f"{settings.API_V1_STR}/facts/mark/{fact.fact_id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["text"] == fact.text
    db.refresh(fact)
    assert user in fact.markers


def assert_success(response):
    assert response.status_code == 200
    return response.json()
