# Se importan las librerías necesarias
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


from . import crud, schema

from ..database import get_db


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
    responses={404: {"description": "Not found"}},
)



# Se contruyen todas las rutas y debajo de ellas el end-point
@router.get("/", response_model=List[schema.Usuarios])
async def get_all_users(db: Session = Depends(get_db)):

    return await crud.get_all_users(db)


@router.get('/usuario/{user_name}', response_model=schema.Usuarios)
async def get_user_by_usuario(user_name: str, db: Session = Depends(get_db)):

    existing_user = await crud.get_user_by_usuario(db, user_name)

    if not existing_user:
        raise HTTPException(status_code=400, detail='El usuario no existe')

    return existing_user


@router.get('/id/{user_id}', response_model=schema.Usuarios)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):

    existing_user = await crud.get_user_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(status_code=400, detail='El id no existe')

    return existing_user


@router.post("/new", response_model=schema.Usuarios)
async def create_user(schema: schema.UsuariosCreate, db: Session = Depends(get_db)):

    existing_user = await crud.get_user_by_usuario(db, schema.usuario)

    if existing_user:
        raise HTTPException(status_code=400, detail='El usuario ya existe')

    return await crud.create_user(db, schema)


@router.delete("/id/{user_id}", response_model=str)
async def delete_user(user_id: int, db: Session = Depends(get_db)):

    existing_user = await crud.get_user_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(status_code=400, detail='El usuario no existe')

    return await crud.delete_user(db, existing_user)


@router.patch("/id/{user_id}/{values}", response_model=str)
async def update_user(user_id: int, values: str, db: Session = Depends(get_db)):

    existing_user = await crud.get_user_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(status_code=400, detail='El usuario no existe')

    return await crud.update_user(db, values, existing_user)
