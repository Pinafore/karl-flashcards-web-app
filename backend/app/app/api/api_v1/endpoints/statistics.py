from datetime import datetime

from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas, interface
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.Statistics)
def read_statistics(
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    statistics = interface.statistics.get_user_stats(user=current_user)
    return statistics


@router.get("/leaderboard", response_model=List[schemas.User])
def read_leaderboard(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    start_date: Optional[datetime] = None,
) -> Any:
    """
    Retrieves users with the most reviews since the specified start time, or all time otherwise
    """

    # top_users = crud.user.get_top_users(db=db, limit=limit, start_date=start_date)

    return []
