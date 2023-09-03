import json
import logging
import time
from datetime import datetime
from typing import List, Union

import requests
from sentry_sdk import capture_exception

from app import models, schemas, crud
from app.core.config import settings
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def change_assignment(user: models.user, repetition_model: schemas.Repetition) -> Union[
    int, requests.exceptions.RequestException, json.decoder.JSONDecodeError]:
    parameters = {'user_id': user.id, 'env': settings.ENVIRONMENT, 'repetition_model': repetition_model}
    try:
        request = requests.put(f"{settings.INTERFACE}api/karl/set_repetition_model/", params=parameters)
        logger.info(request.url)
        return request.status_code
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return e
    except json.decoder.JSONDecodeError as e:
        capture_exception(e)
        return e
