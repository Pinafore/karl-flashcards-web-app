import logging
import time
import numpy as np
from datetime import datetime, date
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pytz import timezone
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.core.config import settings

from app.utils.utils import (
    send_vocab_reminder_email,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Union[schemas.MnemonicLearningFeedbackLog, schemas.MnemonicComparisonFeedbackLog])
def create_mnemonic_log(
        *,
        db: Session = Depends(deps.get_db),
        mnemonic_feedback_in: Union[schemas.MnemonicLearningFeedbackLog, schemas.MnemonicComparisonFeedbackLog],
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Log mnemonic feedback        
    """
    log_type = schemas.Log.mnemonic_comparison_feedback if (type(mnemonic_feedback_in) == schemas.MnemonicComparisonFeedbackLog) else schemas.Log.mnemonic_learning_feedback
    details = mnemonic_feedback_in.dict()
    history_in = schemas.HistoryCreate(
        time=datetime.now(timezone('UTC')).isoformat(),
        user_id=current_user.id,
        log_type=log_type,
        fact_id=mnemonic_feedback_in.fact_id,
        details=details,
    )
    crud.history.create(db=db, obj_in=history_in)

    return mnemonic_feedback_in

@router.post("/feedback_ids", response_model=schemas.MnemonicFeedbackDetailed)
def get_mnemonic_feedback_ids(
        *,
        db: Session = Depends(deps.get_db),
        mnemonic_feedback_in: schemas.MnemonicFeedback,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get feedback IDs
    """
    mnemonic_feedback = crud.mnemonic.get_submitted_feedback_ids(db=db, obj_in=mnemonic_feedback_in)
    if type(mnemonic_feedback) == dict:
        return {
            'user_id': mnemonic_feedback_in.user_id,
            'fact_ids_learning': mnemonic_feedback.get('fact_ids_learning', []),
            'fact_ids_comparison': mnemonic_feedback.get('fact_ids_comparison', [])
        }
    return {
        'user_id': mnemonic_feedback_in.user_id,
        'fact_ids_learning': [],
        'fact_ids_comparison': []
    }

def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix

@router.post("/test_vocab_email")
def test_mnemonic_email(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send email with mnemonic stats
    """
    data = crud.mnemonic.get_users_studying_mnemonics(db)
    email_data = {'num_days_studied_vocab': [], 'num_vocab_studied_total': [], 'num_mnemonics_rated': [], 'user_id': [], 'time_last_studied': [], 'email': [], 'username': []}
    for i in range(len(data)):
        print(f'{i} / {len(data)}')
        user_id, last_time_studied = data[i]
        base_stats = crud.mnemonic.get_mnemonic_stats(db, {'user_id': user_id})
        num_days_studied_vocab = crud.mnemonic.get_vocab_facts_studied_per_day(db, user_id, 20)['num_unique_days']
        user = crud.user.get(db, user_id)

        for k, v in ({'num_days_studied_vocab': num_days_studied_vocab, 'num_vocab_studied_total': base_stats.num_vocab_studied, 'num_mnemonics_rated': base_stats.num_mnemonics_rated, 'user_id': user_id, 'time_last_studied': last_time_studied, 'email': user.email, 'username': user.username}).items():
            email_data[k].append(v)
        time.sleep(5)

    base_reward_idx = np.argsort(-1 * np.array(email_data['num_days_studied_vocab']))
    base_reward_rank = np.argsort(base_reward_idx) + 1

    power_reward_idx = np.argsort(-1 * np.array(email_data['num_mnemonics_rated']))
    power_reward_rank = np.argsort(power_reward_idx) + 1

    email_data['base_reward_rank'] = base_reward_rank
    email_data['power_reward_rank'] = power_reward_rank

    cutoff_datetime = datetime(2024, 2, 26)

    for i in range(len(data)):
        num_days_studied_vocab = email_data['num_days_studied_vocab'][i]
        num_vocab_studied_total = email_data['num_vocab_studied_total'][i]
        num_mnemonics_rated = email_data['num_mnemonics_rated'][i]
        user_id = email_data['user_id'][i]
        time_last_studied = email_data['time_last_studied'][i]
        email = email_data['email'][i]
        username = email_data['username'][i]
        base_rank = email_data['base_reward_rank'][i]
        power_rank = email_data['power_reward_rank'][i]

        if time_last_studied.replace(tzinfo=None) < cutoff_datetime:
            continue

        send_vocab_reminder_email(
            email_to=email,
            username=username,
            num_days_studied_vocab=num_days_studied_vocab,
            num_vocab_studied_total=num_vocab_studied_total,
            num_mnemonics_rated=num_mnemonics_rated,
            base_reward_rank=ordinal(base_rank),
            power_reward_rank=ordinal(power_rank)
        )
        time.sleep(10)

    return 1