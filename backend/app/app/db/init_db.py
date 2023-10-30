import logging

from app import crud, schemas
from app.core.celery_app import celery_app
from app.core.config import settings
from app.db import base  # noqa: F401
from sqlalchemy.orm import Session

from app.schemas import DeckType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        deck = crud.deck.create(db, obj_in=schemas.SuperDeckCreate(title="Default", deck_type=DeckType.public))
        # deck = models.Deck(id=1, title="Default")
        # db.add(deck)
        # db.commit()

        user_in = schemas.SuperUserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            username="KarlMaster",
            is_superuser=True,
        )
        user = crud.user.super_user_create(db, obj_in=user_in)  # noqa: F841

        crud.deck.assign_owner(db, db_obj=deck, user=user)
        logger.info("Sending celery task")
        celery_app.send_task("app.worker.load_jeopardy_facts")
        celery_app.send_task("app.worker.load_quizbowl_facts")
        celery_app.send_task("app.worker.create_test_mode_facts", kwargs={"filename": settings.TEST_MODE_FILE})
