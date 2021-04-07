import logging

from app import models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDHistory(CRUDBase[models.History, schemas.HistoryCreate, schemas.HistoryUpdate]):
    def get_with_debug(self, db: Session, debug_id: str):
        debug = db.query(self.model).filter(self.model.details["debug_id"].astext == debug_id)
        return debug


history = CRUDHistory(models.History)
