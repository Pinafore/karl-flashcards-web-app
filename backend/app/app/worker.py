import itertools
import json
import os
import time
import re

import sentry_sdk
from app import crud, schemas
from app.core.celery_app import celery_app
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from sentry_sdk.integrations.celery import CeleryIntegration
from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Any
from sqlalchemy.orm import Session
from app.utils.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
    send_test_mode_reminder_email,
)

from app.schemas import DeckType

if settings.SENTRY_DSN:
    sentry_sdk.init(settings.SENTRY_DSN, integrations=[CeleryIntegration()])


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


@celery_app.task(acks_late=True)
def remind_test_mode(num_to_send: int, db: Session = Depends(deps.get_db)) -> Any:
    """
    Remind users about test mode performance
    """
    db: Session = SessionLocal()
    # CHANGEEEEE
    data = crud.history.get_test_mode_counts(db).reverse()
    num_done = 0
    num_emails_sent = 0
    for idx, data_item in enumerate(data):
        user, num_studied = data_item
        num_studied -= num_studied // 6
        if num_studied >= 12:
            num_done += 1
            continue
        num_emails_sent += 1
        send_test_mode_reminder_email(
            email_to="matthew.shu@yale.edu",
            username=user.username,
            rank=ordinal(idx + 1),
            num_completed_test_mode=str(num_done),
            num_studied=str(num_studied),
        )
        time.sleep(10)
        if num_emails_sent == num_to_send:
            break
        break

    return {
        "msg": f"Number of test mode reminder emails sent: {num_emails_sent}, out of {len(data)}"
    }


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
                crud.fact.create_fact(db, fact, user, DeckType.public)
                #     deck = crud.deck.find_or_create(db, proposed_deck=fact["deck"], user=user, public=True)
                #     fact_in = schemas.FactCreate(
                #             text=fact["text"],
                #             answer=fact["answer"],
                #             deck_id=deck.id,
                #             answer_lines=fact["answer_lines"],
                #             identifier=fact["identifier"],
                #             category=fact["category"],
                #             extra=fact["extra"]
                #         )
                #     crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
                count = count + 1
        db.close()
        return f"{count} quizbowl questions loaded"
    db.close()
    return f"superuser does not exist yet"


@celery_app.task()
def load_jeopardy_facts() -> str:
    db: Session = SessionLocal()
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if user:
        dirname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(dirname, "./data/jeopardy.json")
        deck = crud.deck.find_or_create(
            db, proposed_deck="Jeopardy", user=user, deck_type=DeckType.public
        )
        with open(filename, "r") as file:
            json_data = json.load(file)
            fact_count = 0
            for fact in itertools.islice(json_data, 0, 20000):
                if "<" not in fact["question"]:
                    extra = {
                        "type": "Jeopardy",
                        "air_date": fact["air_date"],
                        "value": fact["value"],
                        "round": fact["round"],
                        "show_number": fact["show_number"],
                    }
                    fact_in = schemas.FactCreate(
                        text=fact["question"],
                        answer=fact["answer"],
                        deck_id=deck.id,
                        answer_lines=[fact["answer"]],
                        category=fact["category"],
                        extra=extra,
                    )
                    crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
                    fact_count += 1
        db.close()
        return f"{fact_count + 1} quizbowl questions loaded"
    db.close()
    return f"superuser does not exist yet"


@celery_app.task()
def clean_up_preloaded_facts() -> str:
    db: Session = SessionLocal()
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if user:
        count = 0
        facts = crud.fact.get_multi_by_owner(db=db, user=user)
        for fact in facts:
            text = clean_up_text(fact.text)

            fact_update = schemas.FactUpdate(
                text=text,
                answer=fact.answer,
                deck_id=fact.deck_id,
                category=fact.category,
                answer_lines=fact.answer_lines,
                identifier=fact.identifier,
                extra=fact.extra,
            )
            crud.fact.update(db, db_obj=fact, obj_in=fact_update)
            count = count + 1
        db.close()
        return f"{count} facts updated"
    db.close()
    return f"superuser does not exist yet"


def clean_up_text(text) -> str:
    text = text.lstrip('" ')
    text = re.sub(" /$", '"', text)
    text = text.strip("'")
    return text


@celery_app.task()
def create_test_mode_facts(filename: str) -> str:
    db: Session = SessionLocal()
    super_user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if super_user:
        dirname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(dirname, filename)
        message = ""
        with open(filename, "r") as file:
            json_data = json.load(file)
        for item in json_data:
            count = 0
            mode_num = item["mode_num"]

            # Create a test deck for each mode_num
            deck = crud.deck.find_or_create(
                db,
                proposed_deck=f"Test Mode {mode_num}",
                user=super_user,
                deck_type=DeckType.hidden,
            )

            # Create facts for the deck
            for fact in item["questions"]:
                extra = fact.get("extra", {})
                fact_in = schemas.FactCreate(
                    text=fact["text"],
                    answer=fact["answer"],
                    deck_id=deck.id,
                    answer_lines=[fact["answer"]],
                    category=fact["category"],
                    extra=extra,
                )
                crud.fact.create_with_owner(db, obj_in=fact_in, user=super_user)
                count += 1
            message = (
                f"{message}, {count} test mode questions loaded to deck: {deck.title}"
            )
        db.commit()
        crud.deck.assign_test_decks_to_all(db)
        db.commit()
        db.close()
        return message
    db.close()
    return f"superuser does not exist yet"
