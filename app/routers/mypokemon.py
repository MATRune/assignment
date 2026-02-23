from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep

router = APIRouter(prefix="/mypokemon", tags=["mypokemon"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def save_my_pokemon(pokemon_data: dict, db: SessionDep, current_user: AuthDep):
    """Capture a Pokemon for the current user"""
    pokemon_id = pokemon_data.get("pokemon_id")
    name = pokemon_data.get("name")
    
    # Check if Pokemon exists
    pokemon = db.exec(select(Pokemon).where(Pokemon.pokemon_id == pokemon_id)).first()
    
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{pokemon_id} is not a valid pokemon id"
        )
    
    # Create UserPokemon
    user_pokemon = UserPokemon(
        name=name,
        user_id=current_user.id,
        pokemon_id=pokemon.id
    )
    
    db.add(user_pokemon)
    db.commit()
    db.refresh(user_pokemon)
    
    return {"message": f"{name} captured with id: {user_pokemon.id}"}

@router.get("/")
async def list_my_pokemon(db: SessionDep, current_user: AuthDep):
    """List all Pokemon owned by current user"""
    user_pokemon = db.exec(
        select(UserPokemon).where(UserPokemon.user_id == current_user.id)
    ).all()
    
    result = []
    for up in user_pokemon:
        pokemon = db.get(Pokemon, up.pokemon_id)
        result.append({
            "id": up.id,
            "name": up.name,
            "species": pokemon.name
        })
    
    return result

@router.get("/{pokemon_id}")
async def get_my_pokemon(pokemon_id: int, db: SessionDep, current_user: AuthDep):
    """Get specific Pokemon from user's collection"""
    user_pokemon = db.get(UserPokemon, pokemon_id)
    
    if not user_pokemon or user_pokemon.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Id {pokemon_id} is invalid or does not belong to {current_user.username}"
        )
    
    pokemon = db.get(Pokemon, user_pokemon.pokemon_id)
    
    return {
        "id": user_pokemon.id,
        "name": user_pokemon.name,
        "species": pokemon.name
    }

@router.put("/{pokemon_id}")
async def update_my_pokemon(pokemon_id: int, update_data: dict, db: SessionDep, current_user: AuthDep):
    """Rename a Pokemon in user's collection"""
    user_pokemon = db.get(UserPokemon, pokemon_id)
    new_name = update_data.get("name")
    
    if not user_pokemon or user_pokemon.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Id {pokemon_id} is invalid or does not belong to {current_user.username}"
        )
    
    old_name = user_pokemon.name
    user_pokemon.name = new_name
    
    db.add(user_pokemon)
    db.commit()
    db.refresh(user_pokemon)
    
    return {"message": f"{old_name} renamed to {new_name}"}

@router.delete("/{pokemon_id}")
async def delete_my_pokemon(pokemon_id: int, db: SessionDep, current_user: AuthDep):
    """Release a Pokemon from user's collection"""
    user_pokemon = db.get(UserPokemon, pokemon_id)
    
    if not user_pokemon or user_pokemon.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Id {pokemon_id} is invalid or does not belong to {current_user.username}"
        )
    
    pokemon_name = user_pokemon.name
    db.delete(user_pokemon)
    db.commit()
    
    return {"message": f"{pokemon_name} released"}