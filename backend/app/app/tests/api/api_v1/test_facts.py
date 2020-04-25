from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.fact import create_random_fact


def test_create_fact(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/items/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_fact(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    fact = create_random_fact(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{fact.id}", headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == fact.title
    assert content["description"] == fact.description
    assert content["id"] == fact.id
    assert content["owner_id"] == fact.owner_id
