from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.database import SessionDep
from app.models import Pokemon

pokemon_router = APIRouter()

@pokemon_router.get("/pokemon")
async def list_pokemon(session: SessionDep) -> List[dict]:
    pokemons = session.exec(select(Pokemon)).all()
    return [
        {
            "pokemon_id": p.id,
            "name": p.name,
            "attack": p.attack,
            "defense": p.defense,
            "hp": p.hp,
            "height": p.height,
            "weight": p.weight,
            "sp_attack": p.sp_attack,
            "sp_defense": p.sp_defense,
            "speed": p.speed,
            "type1": p.type1,
            "type2": p.type2,
        }
        for p in pokemons
    ]
