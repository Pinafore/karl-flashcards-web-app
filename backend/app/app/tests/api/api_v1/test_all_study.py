import json
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import User
from app.tests.utils.fact import create_random_fact
from app.schemas.fact import FactCreate
from app.tests.utils.utils import random_lower_string, random_email


def test_get_study_set_no_deck(
    client: TestClient, normal_user_token_headers: (Dict[str, str], User), db: Session
) -> None:
    # fact = create_random_fact(db, normal_user_token_headers[1])
    response = client.get(
        f"{settings.API_V1_STR}/study/", headers=normal_user_token_headers[0],
    )
    content = assert_success(response)
    # assert content["text"] == fact.text
    # assert content["fact_id"] == fact.fact_id


def assert_success(response):
    print(response)
    print(response.json())
    assert response.status_code == 200
    return response.json()