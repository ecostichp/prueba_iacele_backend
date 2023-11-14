from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from typing import List

from . import schema, crud

from ..database import get_db


router = APIRouter(
    prefix="/authentication",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.get("/users", response_model=List[schema.Auth])
async def get_all_users(db: Session = Depends(get_db)):

    return await crud.get_users_auth(db)


@router.post("/newuser")
async def create_user(schema: schema.AuthCreate, db: Session = Depends(get_db)):
    existing_user = await crud.get_user_auth_by_user(schema.user, db)

    if existing_user:
        raise HTTPException(status_code=400, detail='El usuario ya existe')

    user_obj = await crud.create_user_auth(schema, db)

    return await crud.create_token(user_obj)


@router.post("/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_authenticated = await crud.authenticate_user(form_data.username, form_data.password, db)

    if not user_authenticated:
        raise HTTPException(
            status_code=401, detail="Usuario y/o Contraseña inválidos")

    return await crud.create_token(user_authenticated)


@router.get("/users/me", response_model=schema.Auth)
async def read_users_me(current_user: schema.Auth = Depends(crud.get_current_user)):

    return current_user
