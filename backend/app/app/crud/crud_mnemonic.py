import json
import logging
import time
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Union, Dict, Any, Optional

import pandas
from fastapi.encoders import jsonable_encoder
from pytz import timezone
from sqlalchemy import or_, and_, func, distinct
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
        # print('\n=========\n')
        # print('Facts with Feedback:', len([x.fact_id for x in db_obj if 'mnemonic_a' not in x.details.keys()]), len([x.fact_id for x in db_obj if 'mnemonic_a' in x.details.keys()]))
        # print('\n=========\n')

        return {'fact_ids_learning': [x.fact_id for x in db_obj if 'mnemonic_a' not in x.details.keys()],
               'fact_ids_comparison': [x.fact_id for x in db_obj if 'mnemonic_a' in x.details.keys()],
                'user_id': obj_in.user_id}
    
    def get_users_studying_mnemonics(self, db: Session):

        results = db.query(
                models.History.user_id, 
                func.max(models.History.time).label('max_time')
            ).filter(
                models.History.log_type.in_([
                    Log.mnemonic_learning_feedback, 
                    Log.mnemonic_comparison_feedback
                ])
            ).group_by(
                models.History.user_id
            ).all()
        
        return results

    
    def get_mnemonic_stats(self, db: Session, parameters: Any) -> schemas.MnemonicStatistics:
        
        base_query = db.query(models.History.fact_id
            ).join(models.Fact, models.Fact.fact_id == models.History.fact_id
            ).filter(models.History.user_id == parameters['user_id']
            ).filter(models.History.log_type.in_([Log.mnemonic_learning_feedback, Log.mnemonic_comparison_feedback])
        )

        if 'date_start' in parameters:
            base_query = base_query.filter(parameters['date_start'] <= models.History.time)
        if 'date_end' in parameters:
            base_query = base_query.filter(models.History.time <= parameters['date_end'])
        if 'deck_id' in parameters:
            base_query = base_query.filter(models.Fact.deck_id == parameters['deck_id'])

        overall_unique_fact_ids = base_query.distinct(models.History.fact_id).count()

        comparison_rating_exists = base_query.filter(
            and_(
                models.History.details.has_key("comparison_rating"),
                models.History.details["comparison_rating"].astext != None
            )
        ).distinct(models.History.fact_id).count()

        user_rating_not_zero = base_query.filter(
            and_(
                models.History.details.has_key("user_rating"),
                models.History.details["user_rating"].astext != "0"
            )
        ).distinct(models.History.fact_id).count()

        return schemas.MnemonicStatistics(
            user_id=parameters['user_id'],
            num_vocab_studied=overall_unique_fact_ids,
            num_mnemonics_rated=comparison_rating_exists + user_rating_not_zero
        )
    
    def get_vocab_facts_studied_per_day(self, db: Session, user_id: int, threshold: int):

        num_unique_days = db.query(
                func.date(models.History.time).label('day'), 
                func.count(distinct(models.History.fact_id)).label('fact_count')
            ).filter(
                models.History.user_id == user_id
            ).filter(
                models.History.log_type.in_([
                    Log.mnemonic_learning_feedback, 
                    Log.mnemonic_comparison_feedback
                ])
            ).group_by(
                'day'
            ).having(
                func.count(distinct(models.History.fact_id)) > threshold
            ).count()
        
        return {'num_unique_days': num_unique_days}
            
mnemonic = CRUDMnemonic(models.Mnemonic)