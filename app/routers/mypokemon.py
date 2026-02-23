from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from app.database import SessionDep
from app.models import UserPokemon, Pokemon
from app.auth import AuthDep

from sqlmodel import select
import csv, os

def _load_pokemon_csv(db_session: Session) -> None:
    if db_session.exec(select(Pokemon)).first():
        return
    csv_path = os.path.join(os.getcwd(), "pokemon.csv")
    try:
        with open(csv_path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
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
                    db_session.add(p)
                except Exception:
                    continue
            db_session.commit()
    except FileNotFoundError:
        pass

router = APIRouter()

@router.get("/mypokemon")
async def list_my_pokemons(
    db: SessionDep,
    user: AuthDep,
):
    records = db.exec(select(UserPokemon).where(UserPokemon.user_id == user.id)).all()
    result = []
    for up in records:
        species = up.pokemon.name if up.pokemon else None
        if not species:
            poke = db.get(Pokemon, up.pokemon_id)
            species = poke.name if poke else None
        result.append({"id": up.id, "name": up.name, "species": species})
    return result


@router.post("/mypokemon", status_code=status.HTTP_201_CREATED)
async def capture_pokemon(
    payload: dict,
    db: SessionDep,
    user: AuthDep,
):
    _load_pokemon_csv(db)
    pokemon_id = payload.get("pokemon_id")
    name = payload.get("name")
    if pokemon_id is None or name is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="pokemon_id and name required")
    pokemon = db.get(Pokemon, pokemon_id)
    if not pokemon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{pokemon_id} is not a valid pokemon id")
    up = UserPokemon(pokemon_id=pokemon_id, name=name, user_id=user.id)
    db.add(up)
    db.commit()
    db.refresh(up)
    return {"message": f"{name} captured with id: {up.id}"}

@router.get("/mypokemon/{id}")
async def get_my_pokemon(
    id: int,
    db: SessionDep,
    user: AuthDep,
):
    up = db.get(UserPokemon, id)
    if not up or up.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Id {id} is invalid or does not belong to {user.username}",
        )
    species = None
    if up.pokemon:
        species = up.pokemon.name
    else:
        pokemon = db.get(Pokemon, up.pokemon_id)
        species = pokemon.name if pokemon else None
    return {"id": up.id, "name": up.name, "species": species}

@router.put("/mypokemon/{id}")
async def update_my_pokemon(
    id: int,
    payload: dict,
    db: SessionDep,
    user: AuthDep,
):
    up = db.get(UserPokemon, id)
    if not up or up.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Id {id} is invalid or does not belong to {user.username}",
        )
    old = up.name
    name = payload.get("name")
    if name is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    up.name = name
    db.add(up)
    db.commit()
    db.refresh(up)
    return {"message": f"{old} renamed to {name}"}

@router.delete("/mypokemon/{id}")
async def delete_my_pokemon(
    id: int,
    db: SessionDep,
    user: AuthDep,
):
    up = db.get(UserPokemon, id)
    if not up or up.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Id {id} is invalid or does not belong to {user.username}",
        )
    name = up.name
    db.delete(up)
    db.commit()
    return {"message": f"{name} released"}
