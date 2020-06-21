from typing import Dict

from app.core.celery_app import celery_app
from app.core.config import settings
from fastapi.testclient import TestClient


def test_celery_worker_test(
        client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {"msg": "test"}
    r = client.post(
        f"{settings.API_V1_STR}/utils/test-celery/",
        json=data,
        headers=superuser_token_headers,
    )
    response = r.json()
    assert response["msg"] == "Word received"


def test_fact_load(
        client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    celery_app.send_task("app.worker.load_quizbowl_facts")
#     db: Session = SessionLocal()
#     user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
#     if user:
#         dirname = os.path.dirname(os.path.abspath(__file__))
#         filename = os.path.join(dirname, '../../../data/formatted.train.clues.json')
#         with open(filename, "r") as file:
#             json_data = json.load(file)
#             # for each_fact in json_data:
#             for each_fact in itertools.islice(json_data, 0, 5):
#                 deck = crud.deck.find_or_create(db, proposed_deck=each_fact["deck"], user=user)
#                 fact_in = schemas.FactCreate(
#                     text=each_fact["text"],
#                     answer=each_fact["answer"],
#                     deck_id=deck.id,
#                     answer_lines=each_fact["answer_lines"],
#                     identifier=each_fact["identifier"],
#                     category=each_fact["category"],
#                     extra=each_fact["extra"]
#                 )
#                 crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
