from typing import Optional

from app import crud
from app.core.security import verify_password
from app.schemas import Repetition
from app.schemas.user import UserCreate, UserUpdate, SuperUserCreate
from app.models.user import User
from app.tests.utils.utils import random_email, random_lower_string
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, username=username, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user = crud.user.authenticate(db, email=email, username=username, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    is_active = crud.user.is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password, is_active=False)
    user = crud.user.create(db, obj_in=user_in)
    is_active = crud.user.is_active(user)
    assert is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = SuperUserCreate(email=email, username=username, password=password, is_superuser=True)
    user = crud.user.super_user_create(db, obj_in=user_in)
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is False


def test_get_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert user.id == user_2.id


def test_update_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


def test_repetition_model_assignment(db: Session) -> None:
    # Declare all existing users are beta testers
    crud.user.make_current_users_beta_testers(db)
    non_beta_count = crud.user.get_count(db, is_beta=False)
    assert non_beta_count == 0
    total_goal = 300
    sm2_init_count = 51
    karl_init_count = 15
    leitner_init_count = 30
    karl50_init_count = 20
    karl85_init_count = 10
    total_init_count = sm2_init_count + karl_init_count + karl50_init_count + karl85_init_count + leitner_init_count
    count = 0
    for _ in range(sm2_init_count):
        create_user(db=db, repetition_model=Repetition.sm2)
        count += 1
    assert count == sm2_init_count
    for _ in range(karl_init_count):
        create_user(db=db, repetition_model=Repetition.karl100)
    for _ in range(leitner_init_count):
        create_user(db=db, repetition_model=Repetition.leitner)
    for _ in range(karl50_init_count):
        create_user(db=db, repetition_model=Repetition.karl50)
    for _ in range(karl85_init_count):
        create_user(db=db, repetition_model=Repetition.karl85)

    schedule_counts = crud.user.get_scheduler_counts(db, is_beta=False)

    assert schedule_counts[Repetition.sm2] == sm2_init_count
    assert schedule_counts[Repetition.leitner] == leitner_init_count
    assert schedule_counts[Repetition.karl100] == karl_init_count
    assert schedule_counts[Repetition.karl50] == karl50_init_count
    assert schedule_counts[Repetition.karl85] == karl85_init_count

    user_create = random_user_create()
    assignment, assignment_method = crud.user.assign_scheduler_to_new_user(db, obj_in=user_create)
    assert isinstance(assignment, Repetition)
    assert assignment_method == "dirichlet"

    # marks the stop of dirichlet assignment
    dirichlet_stop = 250
    each_count = dirichlet_stop / 5
    for _ in range(250 - total_init_count):
        create_user(db=db)
    updated_schedule_counts = crud.user.get_scheduler_counts(db, is_beta=False)
    print(updated_schedule_counts)
    assert each_count - 3 <= updated_schedule_counts[Repetition.sm2] <= each_count + 3
    assert each_count - 3 <= updated_schedule_counts[Repetition.leitner] <= each_count + 3
    assert each_count - 3 <= updated_schedule_counts[Repetition.karl100] <= each_count + 3
    assert each_count - 3 <= updated_schedule_counts[Repetition.karl50] <= each_count + 3
    assert each_count - 3 <= updated_schedule_counts[Repetition.karl85] <= each_count + 3

    for _ in range(total_goal - dirichlet_stop):
        create_user(db=db)
    user_create = random_user_create()
    assignment, assignment_method = crud.user.assign_scheduler_to_new_user(db, obj_in=user_create)
    assert isinstance(assignment, Repetition)
    assert assignment_method == "random"


def create_user(db: Session, repetition_model: Optional[Repetition] = None) -> User:
    email = random_email()
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(email=email, username=username, password=password, is_active=False,
                         repetition_model=repetition_model)
    return crud.user.create(db, obj_in=user_in)


def random_user_create() -> UserCreate:
    return UserCreate(email=random_email(), username=random_lower_string(), password=random_lower_string())
