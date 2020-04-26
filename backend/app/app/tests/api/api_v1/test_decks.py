from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import User
from app.tests.utils.deck import create_random_deck
from app.schemas.deck import DeckCreate, DeckUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_deck(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    data = {"title": "Foo", "public": "false"}
    response = client.post(
        f"{settings.API_V1_STR}/decks/", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    assert content["title"] == data["title"]


def test_read_deck(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    deck = create_random_deck(db, normal_user_token_headers[1])
    response = client.get(
        f"{settings.API_V1_STR}/decks/{deck.id}", headers=normal_user_token_headers[0],
    )
    content = assert_success(response)
    assert content["title"] == deck.title
    assert content["id"] == deck.id


def test_read_decks(
        client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/decks/?limit=5", headers=normal_user_token_headers[0],
    )
    assert_success(response)


def test_read_open_decks(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/decks/public", headers=normal_user_token_headers[0],
    )
    assert_success(response)


def test_assign_deck(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    data = DeckCreate(title="Public", public=True)
    deck = crud.deck.create(db=db, obj_in=data)
    response = client.put(
        f"{settings.API_V1_STR}/decks/?deck_ids={deck.id}", headers=normal_user_token_headers[0], json=data.json(),
    )
    content = assert_success(response)
    assert content[0]["title"] == deck.title


def test_update_deck(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    # data = DeckCreate(title="Public", public=True)
    # deck = crud.deck.create(data)
    deck = create_random_deck(db, normal_user_token_headers[1])
    print(deck.title)
    old_title = deck.title
    new_title = random_lower_string()
    data = {"title": new_title}
    response = client.put(
        f"{settings.API_V1_STR}/decks/{deck.id}", headers=normal_user_token_headers[0], json=data,
    )
    content = assert_success(response)
    db.refresh(deck)
    print("Deck:", deck.title)
    print("content:", content)
    print("old_title:", old_title)
    print("new_title:", new_title)
    assert old_title != content["title"]
    assert new_title == content["title"]
    assert content["title"] == deck.title


def test_delete_deck(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
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