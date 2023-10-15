import json
import logging
import time
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Union, Dict, Any, Optional

import pandas
from fastapi.encoders import jsonable_encoder
from pytz import timezone
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, Query

from app import crud, models, schemas
from app.crud.base import CRUDBase
from app.schemas import Log, DeckType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDMnemonic(CRUDBase[schemas.Mnemonic, schemas.Mnemonic, schemas.Mnemonic]):

    def get(self, db: Session, study_id: Any, fact_id: Any) -> Optional[models.Mnemonic]:
        db_obj = db.query(self.model).filter(models.Mnemonic.fact_id == fact_id and models.Mnemonic.study_id == study_id).first()
        return db_obj
    
    def get_submitted_feedback_ids(self, db: Session, obj_in: schemas.MnemonicFeedback) -> Optional[schemas.MnemonicFeedback]:
        fact_ids = obj_in.fact_ids
        db_obj = db.query(self.model.fact_id).filter(self.model.fact_id.in_(fact_ids), 
                                             self.model.user_rating > 0,
                                             self.model.user_id == obj_in.user_id
                                             ).all()
        return {'fact_ids': [list(r)[0] for r in db_obj], 'user_id': obj_in.user_id}

    def create_with_owner(
            self, db: Session, *, obj_in: schemas.Mnemonic, user: models.User,
    ) -> models.Mnemonic:
        obj_in_data = jsonable_encoder(obj_in)
        now = datetime.now(timezone('UTC')).isoformat()
        db_obj = models.Mnemonic(**obj_in_data, create_date=now)
        db.add(db_obj)
        db.commit()
        return db_obj

mnemonic = CRUDMnemonic(models.Mnemonic)
