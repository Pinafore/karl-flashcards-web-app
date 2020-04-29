import itertools
import json
import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.config import settings

import logging
from app import crud, schemas
from app.db.session import SessionLocal

sentry_sdk.init(
    settings.SENTRY_DSN,
    integrations=[CeleryIntegration()]
)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def load_quizbowl_facts() -> str:
    db: Session = SessionLocal()
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if user:
        dirname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(dirname, './data/formatted.train.clues.json')
        count = 0
        with open(filename, "r") as file:
            json_data = json.load(file)
            for each_fact in json_data:
                deck = crud.deck.find_or_create(db, proposed_deck=each_fact["deck"], user=user)
                fact_in = schemas.FactCreate(
                        text=each_fact["text"],
                        answer=each_fact["answer"],
                        deck_id=deck.id,
                        answer_lines=each_fact["answer_lines"],
                        identifier=each_fact["identifier"],
                        category=each_fact["category"],
                        extra=each_fact["extra"]
                    )
                crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
                count = count + 1
        return f"{count} quizbowl questions loaded"
    return f"superuser does not exist yet"