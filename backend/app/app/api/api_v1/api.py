from app.api.api_v1.endpoints import facts, login, users, utils, decks, study, statistics
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(decks.router, prefix="/decks", tags=["decks"])
api_router.include_router(facts.router, prefix="/facts", tags=["facts"])
api_router.include_router(study.router, prefix="/study", tags=["study"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
