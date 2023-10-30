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


# Values set here are no longer relevant, as they are passed in for each schedule request.
def set_user_settings(user: models.user, new_settings: schemas.UserUpdate) -> Union[
    int, requests.exceptions.RequestException, json.decoder.JSONDecodeError]:
    params = schemas.SetParametersSchema(env=settings.ENVIRONMENT, recall_target=new_settings.recall_target / 100, repetition_model=new_settings.repetition_model)
    parameters = {'user_id': user.id, 'params': params.dict()}
    try:
        request = requests.put(f"{settings.INTERFACE}api/karl/set_params?user_id={user.id}", json=params.dict())
        logger.info(request.url)
        return request.status_code
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return e
    except json.decoder.JSONDecodeError as e:
        capture_exception(e)
        return e
