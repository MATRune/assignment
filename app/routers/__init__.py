from fastapi import APIRouter
main_router = APIRouter()

from .auth import auth_router
from .pokemon import pokemon_router

main_router.include_router(auth_router)
main_router.include_router(pokemon_router)

from app.database import create_db_and_tables

@main_router.get("/init")
async def initialize():
    """Initialize the database and return a confirmation message."""
    # create_db_and_tables is idempotent; it will create missing tables only.
    create_db_and_tables()
    return {"message": "Database Initialized!"}

@main_router.get("/")
async def root():
    return '<h1>Poke API v1.0</h1>'
