import csv
from pathlib import Path
from fastapi import APIRouter, Path
main_router = APIRouter()
from .auth import auth_router
main_router.include_router(auth_router)
from .pokemon import pokemon_router
main_router.include_router(pokemon_router)
from .mypokemon import router as mypokemon_router
main_router.include_router(mypokemon_router)

from app.database import create_db_and_tables

@main_router.get("/init")
async def initialize():
    from app.database import drop_all
    drop_all()
    create_db_and_tables()

    from app.database import engine
    from sqlmodel import Session
    from app.models import Pokemon
    import csv, os

    csv_path = Path.cwd() / "pokemon.csv"
    try:
        with open(csv_path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            with Session(engine) as session:
                for row in reader:
                    try:
                        p = Pokemon(
                            name=row.get("name", ""),
                            attack=int(float(row.get("attack", 0))) if row.get("attack") else 0,
                            defense=int(float(row.get("defense", 0))) if row.get("defense") else 0,
                            hp=int(float(row.get("hp", 0))) if row.get("hp") else 0,
                            height=float(row.get("height_m", 0.0)) if row.get("height_m") else 0.0,
                            weight=float(row.get("weight_kg", 0.0)) if row.get("weight_kg") else 0.0,
                            sp_attack=int(float(row.get("sp_attack", 0))) if row.get("sp_attack") else 0,
                            sp_defense=int(float(row.get("sp_defense", 0))) if row.get("sp_defense") else 0,
                            speed=int(float(row.get("speed", 0))) if row.get("speed") else 0,
                            type1=row.get("type1", "").strip(),
                            type2=row.get("type2", "").strip() or None,
                        )
                        session.add(p)
                    except Exception:
                        continue
                session.commit()
    except FileNotFoundError:
        return {"message": "Database initialized (no CSV file found)"}

    return {"message": "Database Initialized!"}

@main_router.get("/")
async def root():
    return '<h1>Poke API v1.0</h1>'
