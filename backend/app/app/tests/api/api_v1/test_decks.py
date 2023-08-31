from typing import Dict, Tuple

from app import crud
from app.schemas.deck_type import DeckType
from app.core.config import settings
from app.models import User
from app.schemas.deck import SuperDeckCreate
from app.tests.utils.deck import create_random_deck
from app.tests.utils.utils import random_lower_string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    data = {"title": "Foo", "deck_type": "public"}
    response = client.post(
        f"{settings.API_V1_STR}/decks/", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    assert content["title"] == data["title"]


def test_read_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    deck = create_random_deck(db, normal_user_token_headers[1])
    response = client.get(
        f"{settings.API_V1_STR}/decks/{deck.id}", headers=normal_user_token_headers[0],
    )
    content = assert_success(response)
    assert content["title"] == deck.title
    assert content["id"] == deck.id


def test_read_decks(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/decks/?limit=5", headers=normal_user_token_headers[0],
    )
    assert_success(response)


def test_read_open_decks(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/decks/public", headers=normal_user_token_headers[0],
    )
    assert_success(response)


def test_assign_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    data = SuperDeckCreate(title="Public", deck_type=DeckType.public)
    deck = crud.deck.create(db=db, obj_in=data)
    data2 = SuperDeckCreate(title="Public2", deck_type=DeckType.public)
    deck2 = crud.deck.create(db=db, obj_in=data2)
    response = client.put(
        f"{settings.API_V1_STR}/decks/?deck_ids={deck.id}&deck_ids={deck2.id}",
        headers=normal_user_token_headers[0],
        json=data.json(),
    )
    content = assert_success(response)
    user = normal_user_token_headers[1]
    db.refresh(user)
    assert content[0]["title"] == deck.title
    assert content[1]["title"] == deck2.title
    assert deck in user.all_decks
    assert deck2 in user.all_decks


def test_update_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    deck = create_random_deck(db, normal_user_token_headers[1])
    old_title = deck.title
    new_title = random_lower_string()
    data = {"title": new_title}
    response = client.put(
        f"{settings.API_V1_STR}/decks/{deck.id}", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    db.refresh(deck)
    assert old_title != content["title"]
    assert new_title == content["title"]
    assert content["title"] == deck.title


def test_delete_deck(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User], db: Session
) -> None:
    deck = create_random_deck(db, normal_user_token_headers[1])
    user = normal_user_token_headers[1]
    assert user in deck.users
    response = client.delete(
        f"{settings.API_V1_STR}/decks/{deck.id}", headers=normal_user_token_headers[0]
    )
    content = assert_success(response)
    assert content["title"] == deck.title
    db.refresh(deck)
    assert user not in deck.users


def assert_success(response):
    assert response.status_code == 200
    return response.json()
