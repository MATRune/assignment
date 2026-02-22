from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr

class Token(SQLModel):
    access_token: str
    token_type: str
    
class UserPokemon(SQLModel, table=True):
      id: Optional[int] =  Field(default=None, primary_key=True)
      user_id: Optional[int] = Field(default=None, foreign_key="user.id")
      pokemon_id: Optional[int] = Field(default=None, foreign_key="pokemon.id")
      name: Optional[str] = Field(default=None)
      user: Optional["User"] = Relationship(back_populates="user_pokemons")
      pokemon: Optional["Pokemon"] = Relationship(back_populates="user_pokemons")

class User(SQLModel, table=True):
      id: Optional[int] =  Field(default=None, primary_key=True)
      username: str = Field(index=True, unique=True)
      email: str = Field(index=True, unique=True)
      password: str
      user_pokemons: list[UserPokemon] = Relationship(back_populates="user")
      @property
      def pokemon(self):
            return [up.pokemon for up in self.pokemon_collection if up.pokemon]

class Pokemon(SQLModel, table=True):
      id: Optional[int] =  Field(default=None, primary_key=True)
      name: str = Field(index=True)
      attack: int
      defense: int
      hp: int
      height: float
      weight: float
      sp_attack: int 
      sp_defense: int
      speed: int
      type1: str
      type2: Optional[str] = Field(index=None)
      user_pokemons: list[UserPokemon] = Relationship(back_populates="pokemon")
      @property
      def trainer(self):
            if self.user_pokemons and len(self.user_pokemons) > 0:
                  return self.user_pokemons[0].user
            return None