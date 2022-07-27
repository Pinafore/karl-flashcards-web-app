from typing import Dict, Tuple

from app.core.config import settings
from app.models import User
from app.schemas import Schedule, StudySet
from app.tests.utils.deck import create_random_deck
from app.tests.utils.fact import create_random_fact_with_deck
from app.tests.utils.utils import random_lower_string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_study_set_no_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    # fact = create_random_fact(db, normal_user_token_headers[1])
    response = client.get(
        f"{settings.API_V1_STR}/study/", headers=normal_user_token_headers[0],
    )
    assert_success(response)


def test_get_study_set_with_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    deck = create_random_deck(db, user=normal_user_token_headers[1])
    facts = []
    for idx in range(5):
        facts.append(create_random_fact_with_deck(db, user=normal_user_token_headers[1], deck=deck))
    response = client.get(
        f"{settings.API_V1_STR}/study/?deck_id={deck.id}", headers=normal_user_token_headers[0],
    )
    assert_success(response)

# Fix update schedule set test!
def test_update_schedule_set(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    deck = create_random_deck(db, user=normal_user_token_headers[1])
    for _ in range(20):
        fact = create_random_fact_with_deck(db, user=normal_user_token_headers[1], deck=deck)
    response = client.get(
        f"{settings.API_V1_STR}/study/?deck_id={deck.id}", headers=normal_user_token_headers[0],
    )
    data = []
    print(response.json())
    for idx in range(2):
        data.append(Schedule(fact_id=response.json()["unstudied_facts"][idx]["fact_id"],
                             typed=random_lower_string(),
                             response=False,
                             recommendation=False,
                             elapsed_milliseconds_text=10,
                             elapsed_milliseconds_answer=10).dict())
    for idx in range(2):
        data.append(Schedule(fact_id=response.json()["unstudied_facts"][idx]["fact_id"],
                             typed=response.json()["unstudied_facts"][idx]["answer"],
                             response=True,
                             recommendation=True,
                             elapsed_milliseconds_text=10,
                             elapsed_milliseconds_answer=10).dict())
    print(response.json()['id'])
    r = client.put(
        f"{settings.API_V1_STR}/study/?studyset_id={response.json()['id']}", headers=normal_user_token_headers[0], json=data,
    )
    assert_success(response=r)


def test_evaluate_answer(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    deck = create_random_deck(db, user=normal_user_token_headers[1])
    fact = create_random_fact_with_deck(db, user=normal_user_token_headers[1], deck=deck)
    typed = "Avada Kedavra"
    response = client.get(
        f"{settings.API_V1_STR}/study/evaluate?fact_id={fact.fact_id}&typed={typed}",
        headers=normal_user_token_headers[0],
    )
    evaluation = assert_success(response=response)
    assert not evaluation
    typed2 = fact.answer
    response2 = client.get(
        f"{settings.API_V1_STR}/study/evaluate?fact_id={fact.fact_id}&typed={typed2}",
        headers=normal_user_token_headers[0],
    )
    evaluation2 = assert_success(response=response2)
    assert evaluation2


def assert_success(response):
    print(response.text)
    print(response.json())
    assert response.status_code == 200
    return response.json()
