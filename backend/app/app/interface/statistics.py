import json
import logging
from datetime import datetime

import requests
from app import models, schemas
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_stats(user: models.user, *, start_date: datetime = None, end_date: datetime = None) -> schemas.statistics:
    request = requests.get(f"{settings.INTERFACE}api/karl/get_user_stats/{user.id}")
    result = request.json()
    result_dict = json.loads(result)
    statistics = schemas.Statistics(**result_dict, username=user.username)
    return statistics
