from typing import List, Union, Optional

from pydantic import BaseModel

# Properties to return to client about statistics
from app.schemas import User, RankType, Fact


class StudySet(BaseModel):
    facts: List[Fact]
    in_test_mode: bool

# @router.get("/", response_model=schemas.StudySet)
# def get_next_set(
#         db: Session = Depends(deps.get_db),
#         user_id: Optional[int] = None,
#         deck_ids: Optional[List[int]] = Query(None),
#         limit: int = 1,
#         current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Get next set of facts for review using user's schedule.
#     Allows superusers to view anyone's future schedule.
#     A user's deck ids can be provided for filtering.
#     """
#     if user_id:
#         user = crud.user.get(db=db, id=user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         if not (crud.user.is_superuser(current_user) or user_id == current_user.id):
#             raise HTTPException(status_code=400, detail="This user does not have the necessary permissions")
#     else:
#         user = current_user
#
#     if crud.user.test_mode_check(db, db_obj=user):
#         facts = crud.fact.get_test_study_set(db=db, user=user)
#         study_set = schemas.StudySet(facts=facts, test_mode=True)
#     elif deck_ids is None:
#         facts = crud.fact.get_normal_study_set(db=db, user=user, return_limit=limit)
#         study_set = schemas.StudySet(facts=facts, test_mode=False)
#     else:
#         if 2 in deck_ids:
#             raise HTTPException(status_code=557, detail="This deck is currently unavailable")
#         for deck_id in deck_ids:
#             deck = crud.deck.get(db=db, id=deck_id)
#             if not deck:
#                 raise HTTPException(status_code=404, detail="One or more of the specified decks does not exist")
#             if user not in deck.users:
#                 raise HTTPException(status_code=450,
#                                     detail="This user does not have the necessary permission to access one or more"
#                                            " of the specified decks")
#         facts = crud.fact.get_normal_study_set(db=db, user=user, deck_ids=deck_ids, return_limit=limit)
#         study_set = schemas.StudySet(facts=facts, test_mode=False)
#
#     if isinstance(facts, requests.exceptions.RequestException):
#         raise HTTPException(status_code=555, detail="Connection to scheduler is down")
#     if isinstance(facts, json.decoder.JSONDecodeError):
#         raise HTTPException(status_code=556, detail="Scheduler malfunction")
#
#     return study_set
