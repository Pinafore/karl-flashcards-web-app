import json
import logging
import time
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Union, Dict, Any, Optional

import pandas
from fastapi.encoders import jsonable_encoder
from pytz import timezone
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session, Query

from app import crud, models, schemas
from app.crud.base import CRUDBase
from app.schemas import Log, DeckType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDMnemonic(CRUDBase[schemas.MnemonicFeedback, schemas.MnemonicFeedback, schemas.MnemonicFeedback]):
    
    def get_submitted_feedback_ids(self, db: Session, obj_in: schemas.MnemonicFeedback) -> Optional[schemas.MnemonicFeedbackDetailed]:

        fact_ids = obj_in.fact_ids
        db_obj = db.query(models.History).filter(models.History.user_id == obj_in.user_id
                                        ).filter(models.History.log_type.in_([Log.mnemonic_learning_feedback, Log.mnemonic_comparison_feedback])
                                        ).filter(or_(and_(models.History.details.has_key("comparison_rating"), models.History.details["comparison_rating"].astext != None),
                                                     and_(models.History.details.has_key("user_rating"), models.History.details["user_rating"].astext != "0"))
                                        ).filter(models.History.fact_id.in_(fact_ids)
                                        ).all()
        
        return {'fact_ids_learning': [x.fact_id for x in db_obj if 'mnemonic_a' not in x.details.keys()],
               'fact_ids_comparison': [x.fact_id for x in db_obj if 'mnemonic_a' in x.details.keys()],
                'user_id': obj_in.user_id}

mnemonic = CRUDMnemonic(models.Mnemonic)