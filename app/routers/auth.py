from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from typing import Annotated

from app.database import SessionDep          # make sure this is the name of your session dependency
from app.models import User, Token           # explicitly import the models we need
from app.auth import verify_password, create_access_token, encrypt_password
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

auth_router = APIRouter()

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep
) -> Token:
    # look up the user by username
    user = db.exec(select(User).where(User.username == form_data.username)).one_or_none()
    if not user or not verify_password(plaintext_password=form_data.password, encrypted_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


# extra endpoints for user management used by tests
@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: SessionDep):
    existing = db.exec(
        select(User).where((User.username == user.username) | (User.email == user.email))
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username or email already exists")
    new_user = User(
        username=user.username,
        email=user.email,
        password=encrypt_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"{new_user.username} created"}

@auth_router.post("/login", response_model=Token)
async def login(request: Request, db: SessionDep):
    # the client is expected to supply a username and password; tests/collections
    # may send the payload as JSON or as form data (and sometimes even with an
    # incorrect Content-Type header).  We therefore read the raw body and try to
    # interpret it as JSON first, falling back to FastAPI's form parser if that
    # fails.  Regardless of how the data is supplied we end up with a simple
    # dictionary containing the credentials.
    data: dict[str, str]
    try:
        data = await request.json()
    except Exception:
        # `request.form()` will only work if the incoming content type is one of
        # the form encodings; in the failing postman test the header is wrong so
        # we catch any exception and try to coerce things ourselves.
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            data = {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        # if the credentials are missing or cannot be read we treat it as bad
        # credentials to allow the test to receive the expected 401 response
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="bad username/password given")

    found = db.exec(select(User).where(User.username == username)).one_or_none()
    if not found or not verify_password(plaintext_password=password, encrypted_password=found.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="bad username/password given")

    access_token = create_access_token(data={"sub": found.username})
    return Token(access_token=access_token, token_type="bearer")