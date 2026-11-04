# Se importan las librerías necesarias
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from . import schema, crud
from ..database import SessionDep


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/authentication",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

#Quitar este endpoint cuando se tenga trabajado el tema de autenticación y promoción de usuarios (empleados)
from sqlmodel  import select
@router.get('/', response_model=list[schema.AuthenticationsPublic])
async def wep_all(session: SessionDep):

    return session.exec(select(schema.Authentications)).all()
#Quitar hasta aquí




@router.post("/new", response_model=schema.Authentications)
async def post_obj(new_obj: schema.AuthenticationsCreate, session: SessionDep):

    existing_obj = await crud.read_by_username(new_obj.username, session)

    if existing_obj:
        raise HTTPException(status_code=400, detail='El usuario ya existe')

    return await crud.create(new_obj, session)


@router.post("/token")
async def generate_token(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user_authenticated = await crud.authenticate_user(form_data.username, form_data.password, session)

    if not user_authenticated:
        raise HTTPException(
            status_code=401, detail="Usuario y/o Contraseña inválidos")

    return await crud.create_token(user_authenticated)


@router.get("/user/me", response_model=schema.AuthenticationsPublic)
async def read_authenticated_me(current_user:  Annotated[schema.Authentications, Depends(crud.require_user_authenticated)]):

    return current_user
