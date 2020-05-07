import json
from datetime import datetime
from typing import List, Optional

import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app import crud, models, schemas

import logging

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_stats(user: models.user, *, start_date: datetime = None, end_date: datetime = None) -> schemas.statistics:
    request = requests.get(f"{settings.INTERFACE}api/karl/get_user_stats/{user.id}")
    result = request.json()
    result_dict = json.loads(result)
    statistics = schemas.Statistics(**result_dict, username=user.username)
    return statistics

