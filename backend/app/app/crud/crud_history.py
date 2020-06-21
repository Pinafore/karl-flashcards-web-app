import logging

from app import models, schemas
from app.crud.base import CRUDBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDHistory(CRUDBase[models.History, schemas.HistoryCreate, schemas.HistoryUpdate]):
    pass


history = CRUDHistory(models.History)
