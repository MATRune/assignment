from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr

class Token(SQLModel):
    access_token: str
    token_type: str
    
class UserPokemon(SQLModel, table=True):
      id: Optional[int] =  Field(default=None, primary_key=True)
      pass

class User(SQLModel, table=True):
      id: Optional[int] =  Field(default=None, primary_key=True)
      pass

class Pokemon(SQLModel, table=True):
      id: Optional[int] =  Field(default=None, primary_key=True)
      pass