import json
import logging
from datetime import datetime
from typing import List, Union

import requests
from sentry_sdk import capture_exception

from app import models, schemas, crud
from app.core.config import settings
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_stats(db: Session, user: models.user, *, date_start: datetime = None, date_end: datetime = None,
                   deck_id: int = None) -> Union[
    schemas.Statistics, requests.exceptions.RequestException, json.decoder.JSONDecodeError]:
    parameters = {'user_id': user.id, 'env': settings.ENVIRONMENT}
    if date_start:
        parameters['date_start'] = date_start
    if date_end:
        parameters['date_end'] = date_end
    if deck_id:
        parameters['deck_id'] = deck_id
    try:
        request = requests.get(f"{settings.INTERFACE}api/karl/get_user_stats/", params=parameters)
        logger.info(request.url)
        result_dict = request.json()

        name = create_name(db, date_start, date_end, deck_id)
        statistics = schemas.Statistics(**result_dict, user=user, name=name)
        return statistics
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return e
    except json.decoder.JSONDecodeError as e:
        capture_exception(e)
        return e


def get_leaderboard(db: Session, rank_type: schemas.RankType, user: models.user, *, skip: int = None, limit: int = 10,
                    min_studied: int = 10, deck_id: int = None, date_start: datetime = None,
                    date_end: datetime = None) -> Union[schemas.Leaderboard,
                                                        requests.exceptions.RequestException,
                                                        json.decoder.JSONDecodeError]:
    if rank_type == schemas.RankType.known_rate \
            or rank_type == schemas.RankType.new_known_rate \
            or rank_type == schemas.RankType.review_known_rate:
        min_studied = 50
    parameters = {'rank_type': rank_type, 'skip': skip, 'limit': limit, 'min_studied': min_studied,
                  'env': settings.ENVIRONMENT, 'user_id': user.id}
    if skip:
        parameters['skip'] = skip
    if deck_id:
        parameters['deck_id'] = deck_id
    if date_start:
        parameters['date_start'] = date_start
    if date_end:
        parameters['date_end'] = date_end
    try:
        request = requests.get(f"{settings.INTERFACE}api/karl/leaderboard/", params=parameters)
        logger.info(request.url)
        data = request.json()

        name = create_name(db, date_start, date_end, deck_id)
        details = create_details(rank_type, min_studied)
        headers = [schemas.DataTypeHeader(text="Rank", value="rank"),
                   schemas.DataTypeHeader(text="User", value="user.username"),
                   ]
        if rank_type == schemas.RankType.total_seen:
            headers.append(schemas.DataTypeHeader(text="Total Studied", value="value"))
        elif rank_type == schemas.RankType.new_facts:
            headers.append(schemas.DataTypeHeader(text="New Facts Studied", value="value"))
        elif rank_type == schemas.RankType.reviewed_facts:
            headers.append(schemas.DataTypeHeader(text="Reviewed Facts Studied", value="value"))
        elif rank_type == schemas.RankType.known_rate:
            headers.append(schemas.DataTypeHeader(text="Total Recall (%)", value="value"))
        elif rank_type == schemas.RankType.new_known_rate:
            headers.append(schemas.DataTypeHeader(text="New Fact Recall (%)", value="value"))
        elif rank_type == schemas.RankType.review_known_rate:
            headers.append(schemas.DataTypeHeader(text="Reviewed Fact Recall (%)", value="value"))
        elif rank_type == schemas.RankType.total_minutes:
            headers.append(schemas.DataTypeHeader(text="Minutes Spent", value="value"))
        elif rank_type == schemas.RankType.elapsed_minutes_text:
            headers.append(schemas.DataTypeHeader(text="Minutes Spent on Front", value="value"))
        leaderboard = schemas.Leaderboard(
            leaderboard=[schemas.LeaderboardUser(user=crud.user.get(db=db, id=user["user_id"]), value=user["value"],
                                                 rank=user["rank"]) for
                         user in data["leaderboard"]],
            total=data["total"], name=name, rank_type=rank_type,
            headers=headers, details=details, user_place=data["user_place"])
        if data["user_id"]:
            leaderboard.user = crud.user.get(db=db, id=data["user_id"])
        return leaderboard
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return e
    except json.decoder.JSONDecodeError as e:
        capture_exception(e)
        return e


def create_name(db: Session, date_start: datetime = None, date_end: datetime = None, deck_id: int = None):
    name = ""
    if date_start:
        date_start = date_start.astimezone()
    if date_end:
        date_end = date_end.astimezone()

    if deck_id:
        deck = crud.deck.get(db=db, id=deck_id)
        name = deck.title + ": "
    if date_start and date_end:
        if date_start.date() == date_end.date():
            name = name + date_start.strftime("%m/%d/%y")
        else:
            name = name + date_start.strftime("%m/%d/%y") + " - " + date_end.strftime("%m/%d/%y")
    elif date_start:
        now = datetime.now(tz=date_start.tzinfo)
        if now.date() == date_start.date():
            name = name + "Today"
        else:
            name = name + date_start.strftime("%m/%d/%y") + " - Present"
    elif date_end:
        name = name + "Until " + date_end.strftime("%m/%d/%y")
    elif deck_id:
        name = name + "All Time"
    else:
        name = "All Time"
    return name


def create_details(rank_type: schemas.RankType, min_studied: int):
    details = f"Minimum {min_studied} facts reviewed\nRank Type: {rank_type}"
    return details
