from typing import Dict, Tuple

from app import crud
from app.core.config import settings
from app.models import User
from app.schemas import UserCreate
from app.tests.utils.utils import random_lower_string, random_email
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


#
def test_get_users_superuser_me(
        client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is True
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers[0])
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(
        client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password, "username": username}
    r = client.post(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = crud.user.get_by_email(db, email=email)
    assert user
    assert user.email == created_user["email"]
    assert user.username == created_user["username"]


def test_get_existing_user(
        client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, username=username)
    user = crud.user.create(db, obj_in=user_in)
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.user.get_by_email(db, email=email)
    assert existing_user
    assert existing_user.email == api_user["email"]
    assert existing_user.username == api_user["username"]


def test_create_user_existing_email(
        client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, username=username)
    crud.user.create(db, obj_in=user_in)
    data = {"email": email, "password": password, "username": username}
    r = client.post(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


def test_create_user_by_normal_user(
        client: TestClient, normal_user_token_headers: Tuple[Dict[str, str], User]
) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password, "username": username}
    r = client.post(
        f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers[0], json=data,
    )
    assert r.status_code == 400


def test_retrieve_users(
        client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, username=username)
    crud.user.create(db, obj_in=user_in)

    username2 = random_lower_string()
    email2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=email2, password=password2, username=username2)
    crud.user.create(db, obj_in=user_in2)

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users) > 1
    for fact in all_users:
        assert "email" in fact
