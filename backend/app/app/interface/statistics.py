import json
import time
from datetime import datetime
from typing import List, Union

import requests
from sentry_sdk import capture_exception

from app import models, schemas, crud
from app.core.config import settings
from sqlalchemy.orm import Session

from app.utils.utils import logger, log_time, time_it


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

        mnemonic_statistics = crud.mnemonic.get_mnemonic_stats(db, parameters)
        print(mnemonic_statistics)
        result_dict['num_vocab_studied'] = mnemonic_statistics.num_vocab_studied
        result_dict['num_mnemonics_rated'] = mnemonic_statistics.num_mnemonics_rated

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
        begin_overall_start = time.time()
        request = requests.get(f"{settings.INTERFACE}api/karl/leaderboard/", params=parameters)
        data = request.json()
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("get leaderboard: " + str(overall_total_time))

        begin_overall_start = time.time()
        name = create_name(db, date_start, date_end, deck_id)
        details = create_details(min_studied, rank_type)
        headers = [schemas.DataTypeHeader(text="Rank", value="rank", width="1%"),
                   schemas.DataTypeHeader(text="User", value="user.username", width="30%"),
                   ]
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("create details: " + str(overall_total_time))
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
        elif rank_type == schemas.RankType.n_days_studied:
            headers.append(schemas.DataTypeHeader(text="Days Studied", value="value"))
        elif rank_type == schemas.RankType.num_vocab_studied:
            headers.append(schemas.DataTypeHeader(text="Vocab Facts Studied", value="value"))
        elif rank_type == schemas.RankType.num_mnemonics_rated:
            headers.append(schemas.DataTypeHeader(text="Mnemonics Rated", value="value"))
        begin_overall_start = time.time()

        leaderboard = schemas.Leaderboard(
            leaderboard=[schemas.LeaderboardUser(user=crud.user.get(db=db, id=user["user_id"]), value=user["value"],
                                                 rank=user["rank"]) for
                         user in data["leaderboard"] if crud.user.get(db=db, id=user["user_id"])],
            total=data["total"], name=name, rank_type=rank_type,
            headers=headers, details=details, user_place=data["user_place"])
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("create leaderboard: " + str(overall_total_time))
        if data["user_id"]:
            leaderboard.user = crud.user.get(db=db, id=data["user_id"])
        return leaderboard
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return e
    except json.decoder.JSONDecodeError as e:
        capture_exception(e)
        return e


def get_leaderboard_local(db: Session, rank_type: schemas.RankType, user: models.user, *, skip: int = None, limit: int = 10,
                         min_studied: int = 10, deck_id: int = None, date_start: datetime = None,
                         date_end: datetime = None) -> schemas.Leaderboard:
    """
    Local leaderboard implementation that doesn't rely on external scheduler service
    """
    from sqlalchemy import func, and_, or_
    from app.models.history import History
    from app.models.fact import Fact
    from app.models.user import User
    from app.schemas.log import Log
    
    # Base query for study history
    query = db.query(History).filter(History.log_type == Log.study)
    
    # Apply date filters
    if date_start:
        query = query.filter(History.time >= date_start)
    if date_end:
        query = query.filter(History.time <= date_end)
    
    # Apply deck filter if specified
    if deck_id:
        query = query.join(Fact).filter(Fact.deck_id == deck_id)
    
    # Calculate different metrics based on rank_type
    if rank_type == schemas.RankType.total_seen:
        # Count total facts studied
        user_stats = query.with_entities(
            History.user_id,
            func.count(History.fact_id.distinct()).label('value')
        ).group_by(History.user_id).having(func.count(History.fact_id.distinct()) >= min_studied).all()
        
    elif rank_type == schemas.RankType.new_facts:
        # Count new facts studied (first time studying each fact)
        subquery = db.query(History.fact_id, History.user_id, func.min(History.time).label('first_study'))\
            .filter(History.log_type == Log.study)\
            .group_by(History.fact_id, History.user_id).subquery()
        
        user_stats = db.query(subquery.c.user_id, func.count(subquery.c.fact_id).label('value'))\
            .group_by(subquery.c.user_id)\
            .having(func.count(subquery.c.fact_id) >= min_studied).all()
            
    elif rank_type == schemas.RankType.reviewed_facts:
        # Count reviewed facts (studied more than once)
        subquery = db.query(History.fact_id, History.user_id, func.count(History.id).label('study_count'))\
            .filter(History.log_type == Log.study)\
            .group_by(History.fact_id, History.user_id)\
            .having(func.count(History.id) > 1).subquery()
        
        user_stats = db.query(subquery.c.user_id, func.count(subquery.c.fact_id).label('value'))\
            .group_by(subquery.c.user_id)\
            .having(func.count(subquery.c.fact_id) >= min_studied).all()
            
    elif rank_type == schemas.RankType.known_rate:
        # Calculate overall accuracy rate
        user_stats = query.with_entities(
            History.user_id,
            func.count(History.id).label('total'),
            func.sum(func.cast(History.correct, Integer)).label('correct')
        ).group_by(History.user_id).having(func.count(History.id) >= min_studied).all()
        
        # Calculate percentage
        user_stats = [(stat.user_id, (stat.correct / stat.total * 100) if stat.total > 0 else 0) 
                      for stat in user_stats if stat.total >= min_studied]
        
    elif rank_type == schemas.RankType.total_minutes:
        # Calculate total study time in minutes
        user_stats = query.with_entities(
            History.user_id,
            func.sum(func.cast(History.details['elapsed_milliseconds_text'].astext, Integer) + 
                    func.cast(History.details['elapsed_milliseconds_answer'].astext, Integer)).label('value')
        ).group_by(History.user_id).having(func.count(History.id) >= min_studied).all()
        
        # Convert milliseconds to minutes
        user_stats = [(stat.user_id, stat.value / 60000) for stat in user_stats if stat.value is not None]
        
    else:
        # Default to total_seen for unsupported rank types
        user_stats = query.with_entities(
            History.user_id,
            func.count(History.fact_id.distinct()).label('value')
        ).group_by(History.user_id).having(func.count(History.fact_id.distinct()) >= min_studied).all()
    
    # Sort by value descending and apply pagination
    user_stats.sort(key=lambda x: x[1], reverse=True)
    
    # Apply skip and limit
    if skip:
        user_stats = user_stats[skip:]
    if limit:
        user_stats = user_stats[:limit]
    
    # Get user objects and create leaderboard
    leaderboard_users = []
    for rank, (user_id, value) in enumerate(user_stats, 1):
        user_obj = crud.user.get(db=db, id=user_id)
        if user_obj:
            leaderboard_users.append(schemas.LeaderboardUser(
                user=user_obj,
                value=value,
                rank=rank
            ))
    
    # Find current user's place
    user_place = None
    current_user_stats = None
    for rank, (user_id, value) in enumerate(user_stats, 1):
        if user_id == user.id:
            user_place = rank
            current_user_stats = (user_id, value)
            break
    
    # Create headers
    headers = [schemas.DataTypeHeader(text="Rank", value="rank", width="1%"),
               schemas.DataTypeHeader(text="User", value="user.username", width="30%")]
    
    if rank_type == schemas.RankType.total_seen:
        headers.append(schemas.DataTypeHeader(text="Total Studied", value="value"))
    elif rank_type == schemas.RankType.new_facts:
        headers.append(schemas.DataTypeHeader(text="New Facts Studied", value="value"))
    elif rank_type == schemas.RankType.reviewed_facts:
        headers.append(schemas.DataTypeHeader(text="Reviewed Facts Studied", value="value"))
    elif rank_type == schemas.RankType.known_rate:
        headers.append(schemas.DataTypeHeader(text="Total Recall (%)", value="value"))
    elif rank_type == schemas.RankType.total_minutes:
        headers.append(schemas.DataTypeHeader(text="Minutes Spent", value="value"))
    else:
        headers.append(schemas.DataTypeHeader(text="Value", value="value"))
    
    # Create name and details
    name = create_name(db, date_start, date_end, deck_id)
    details = create_details(min_studied, rank_type)
    
    # Create leaderboard
    leaderboard = schemas.Leaderboard(
        leaderboard=leaderboard_users,
        total=len(user_stats),
        name=name,
        rank_type=rank_type,
        headers=headers,
        details=details,
        user_place=user_place,
        skip=skip or 0,
        limit=limit
    )
    
    # Add current user if they're in the leaderboard
    if current_user_stats:
        leaderboard.user = crud.user.get(db=db, id=current_user_stats[0])
    
    return leaderboard


def create_name(db: Session, date_start: datetime = None, date_end: datetime = None, deck_id: int = None):
    name = ""

    if deck_id:
        deck = crud.deck.get(db=db, id=deck_id)
        name = deck.title + ": "

    now = datetime.now(tz=date_start.tzinfo) if date_start else None

    if date_start and date_end:
        if date_start.date() == date_end.date():
            if now.date() == date_start.date():
                name = name + "Today"
            else:
                name = name + date_start.strftime("%m/%d/%y")
        else:
            name = name + date_start.strftime("%m/%d/%y") + " - " + date_end.strftime("%m/%d/%y")
    elif date_start:
        logger.info(now.date())
        logger.info(date_start.date())
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


def create_details(min_studied: int, rank_type: schemas.RankType):
    if rank_type == schemas.RankType.n_days_studied:
        details = f"Minimum {min_studied} Facts Reviewed Each Day"
    else:
        details = f"Minimum {min_studied} Facts Reviewed"
    return details
