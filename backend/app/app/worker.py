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
        filename = os.path.join(dirname, "./data/formatted.train.clues.json")
        count = 0
        with open(filename, "r") as file:
            json_data = json.load(file)
            for fact in json_data:
                deck = crud.deck.find_or_create(db, proposed_deck=fact["deck"], user=user, public=True)
                fact_in = schemas.FactCreate(
                        text=fact["text"],
                        answer=fact["answer"],
                        deck_id=deck.id,
                        answer_lines=fact["answer_lines"],
                        identifier=fact["identifier"],
                        category=fact["category"],
                        extra=fact["extra"]
                    )
                crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
                count = count + 1
        return f"{count} quizbowl questions loaded"
    return f"superuser does not exist yet"

@celery_app.task()
def load_jeopardy_facts() -> str:
    db: Session = SessionLocal()
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if user:
        dirname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(dirname, "./data/jeopardy.json")
        deck = crud.deck.find_or_create(db, proposed_deck="Jeopardy", user=user, public=True)
        with open(filename, "r") as file:
            json_data = json.load(file)
            for count, fact in enumerate(itertools.islice(json_data, 0, 20000)):
                if "<" not in fact["question"]:
                    extra = {
                        "type": "Jeopardy",
                        "air_date": fact["air_date"],
                        "value": fact["value"],
                        "round": fact["round"],
                        "show_number": fact["show_number"]
                    }
                    fact_in = schemas.FactCreate(
                            text=fact["question"],
                            answer=fact["answer"],
                            deck_id=deck.id,
                            answer_lines=[fact["answer"]],
                            category=fact["category"],
                            extra=extra
                        )
                    crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
        return f"{count+1} quizbowl questions loaded"
    return f"superuser does not exist yet"