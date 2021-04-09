from datetime import datetime, timedelta
from typing import Any, List, Optional

import json
import requests
from fastapi import APIRouter, Depends, HTTPException
from pytz import timezone
from sqlalchemy.orm import Session

from app import models, schemas, interface, crud
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.Statistics)
def read_statistics(
        *,
        db: Session = Depends(deps.get_db),
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        deck_id: Optional[int] = None,
        current_user: models.User = Depends(deps.get_current_active_user),
):
    statistics = interface.statistics.get_user_stats(db=db, user=current_user, date_start=date_start, date_end=date_end,
                                                     deck_id=deck_id)
    if isinstance(statistics, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(statistics, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")
    return statistics


@router.get("/home", response_model=List[schemas.Statistics])
def read_home_statistics(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    today = datetime.now(timezone('UTC')) - timedelta(days=1)
    stat = interface.statistics.get_user_stats(db=db, user=current_user, date_start=today)
    stat.name = "Last 24 Hours"
    if isinstance(stat, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(stat, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")

    seven_days = datetime.now(timezone('UTC')) - timedelta(days=7)
    seven_stat = interface.statistics.get_user_stats(db=db, user=current_user, date_start=seven_days)
    seven_stat.name = "Last 7 Days"
    if isinstance(seven_stat, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(seven_stat, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")

    total_stat = interface.statistics.get_user_stats(db=db, user=current_user)
    if isinstance(total_stat, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(total_stat, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")
    return [stat, seven_stat, total_stat]


@router.get("/saved", response_model=List[schemas.Statistics])
def read_saved_statistics(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    today = datetime.now(timezone('UTC')) - timedelta(days=1)
    stat = interface.statistics.get_user_stats(db=db, user=current_user, date_start=today)
    stat.name = "Last 24 Hours"
    if isinstance(stat, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(stat, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")

    seven_days = datetime.now(timezone('UTC')) - timedelta(days=7)
    seven_stat = interface.statistics.get_user_stats(db=db, user=current_user, date_start=seven_days)
    seven_stat.name = "Last 7 Days"
    if isinstance(seven_stat, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(seven_stat, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")

    total_stat = interface.statistics.get_user_stats(db=db, user=current_user)
    if isinstance(total_stat, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(total_stat, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")
    return [stat, seven_stat, total_stat]


@router.get("/leaderboard", response_model=schemas.Leaderboard)
def read_leaderboard(
        *,
        db: Session = Depends(deps.get_db),
        rank_type: schemas.RankType,
        skip: int = None,
        limit: int = 10,
        min_studied: int = 10,
        deck_id: int = None,
        date_start: datetime = None,
        date_end: datetime = None,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves leaderboard of users since the specified start time, or all time otherwise
    """

    top_users = interface.statistics.get_leaderboard(db=db, user=current_user, rank_type=rank_type, skip=skip,
                                                     limit=limit,
                                                     min_studied=min_studied, deck_id=deck_id, date_start=date_start,
                                                     date_end=date_end)
    if isinstance(top_users, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(top_users, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")
    return top_users


@router.get("/typed", response_model=str)
def read_historical_fact(
        *,
        db: Session = Depends(deps.get_db),
        history_id: int = None,
        debug_id: str = None,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieves user typed answer for event
    """
    if history_id:
        history_instance = crud.history.get(db=db, id=history_id)
    elif debug_id:
        history_instance = crud.history.get_with_debug(db=db, debug_id=debug_id)
    else:
        raise HTTPException(status_code=408, detail="Missing either history_id or debug_id")

    if "typed" in history_instance.details:
        return history_instance.details["typed"]
    else:
        raise HTTPException(status_code=408, detail="Typed response missing (history instance is not a study)")
