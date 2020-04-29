import json
from typing import List, Union, Dict, Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app import crud, models, schemas, evaluate
from datetime import datetime
from pytz import timezone
import time
import requests

import logging

from app.schemas import Permission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDHistory(CRUDBase[models.History, schemas.HistoryCreate, schemas.HistoryUpdate]):
    pass


history = CRUDHistory(models.History)
