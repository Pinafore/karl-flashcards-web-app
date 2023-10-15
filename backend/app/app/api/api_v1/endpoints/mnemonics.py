import logging
import time
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

@router.post("/", response_model=schemas.Mnemonic)
def create_mnemonic(
        *,
        db: Session = Depends(deps.get_db),
        mnemonic_in: schemas.Mnemonic,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new mnemonic data.
    """
    mnemonic = crud.mnemonic.create_with_owner(db=db, obj_in=mnemonic_in, user=current_user)
    return {
        'study_id': mnemonic.study_id,
        'fact_id': mnemonic.fact_id,
        'user_id': mnemonic.user_id,
        'user_rating': mnemonic.user_rating,
        'viewed_mnemonic': mnemonic.viewed_mnemonic,
        'is_bad_keyword_link': mnemonic.is_bad_keyword_link,
        'is_difficult_to_understand': mnemonic.is_difficult_to_understand,
        'is_incorrect_definition': mnemonic.is_incorrect_definition,
        'is_offensive': mnemonic.is_offensive,
        'correct': mnemonic.correct
    }

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