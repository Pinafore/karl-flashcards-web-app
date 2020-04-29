from datetime import datetime

import requests

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app import crud, models, schemas, evaluate
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.Statistics)
def read_statistics(
    *,
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    return schemas.Statistics(user_id=1, new_facts=0, reviewed_facts=0, total_seen=0, total_seconds=0)

@router.get("/leaderboard", response_model=List[models.User])
def read_leaderboard(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    start_date: datetime = None,
) -> Any:
    """
    Retrieves users with the most reviews since the specified start time, or all time otherwise
    """

    # top_users = crud.user.get_top_users(db=db, limit=limit, start_date=start_date)

    return []
