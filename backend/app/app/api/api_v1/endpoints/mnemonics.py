import logging
import time
import json
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pytz import timezone
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=schemas.MnemonicLearningFeedbackLog or schemas.MnemonicComparisonFeedbackLog)
def create_mnemonic_log(
        *,
        db: Session = Depends(deps.get_db),
        mnemonic_feedback_in: schemas.MnemonicLearningFeedbackLog or schemas.MnemonicComparisonFeedbackLog,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new mnemonic data.
    """
    #mnemonic = crud.mnemonic.create_with_owner(db=db, obj_in=mnemonic_in, user=current_user)

    log_type = schemas.log.comparison_feedback if (type(mnemonic_feedback_in) == schemas.MnemonicComparisonFeedbackLog) else schemas.log.mnemonic_individual_feedback
    details = json.dumps(mnemonic_feedback_in.to_dict())
    history_in = schemas.HistoryCreate(
        time=datetime.now(timezone('UTC')).isoformat(),
        user_id=current_user.id,
        log_type=log_type,
        fact_id=mnemonic_feedback_in.fact_id,
        details=details,
    )
    crud.history.create(db, history_in)

    return mnemonic_feedback_in

@router.post("/feedback_ids", response_model=schemas.MnemonicFeedback)
def get_mnemonic_feedback_ids(
        *,
        db: Session = Depends(deps.get_db),
        mnemonic_feedback_in: schemas.MnemonicFeedback,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new mnemonic data.
    """
    mnemonic_feedback = crud.mnemonic.get_submitted_feedback_ids(db=db, obj_in=mnemonic_feedback_in)
    if type(mnemonic_feedback) == dict:
        return {
            'user_id': mnemonic_feedback_in.user_id,
            'fact_ids': mnemonic_feedback.get('fact_ids', [])
        }
    return {
        'user_id': mnemonic_feedback_in.user_id,
        'fact_ids': []
    }