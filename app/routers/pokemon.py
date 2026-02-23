from fastapi import APIRouter
from sqlmodel import select
from app.database import SessionDep
from app.models import Pokemon

router = APIRouter(prefix="/pokemon", tags=["pokemon"])

@router.get("/")
async def list_pokemon(db: SessionDep):
    """List all Pokemon"""
    pokemon = db.exec(select(Pokemon)).all()
    
    # Format response according to Postman tests
    result = []
    for p in pokemon:
        result.append({
            "pokemon_id": p.pokemon_id,
            "name": p.name,
            "attack": p.attack,
            "defense": p.defense,
            "sp_attack": p.sp_attack,
            "sp_defense": p.sp_defense,
            "speed": p.speed,
            "hp": p.hp,
            "height": p.height,
            "weight": p.weight,
            "type1": p.type1,
            "type2": p.type2
        })
    
    return result