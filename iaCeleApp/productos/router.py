# Se importan las librerías necesarias
from fastapi import APIRouter, HTTPException, Query
from typing import Annotated

from . import schema, crud
from ..database import SessionDep
from ..authentication import authentication_require


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
    # dependencies=[authentication_require]
)


@router.post("/new", response_model=schema.Products)
async def post_obj(new_obj: schema.ProductsCreate, session: SessionDep):

    existing_obj = await crud.read_by_key(new_obj.id_odoo, session)

    if existing_obj:
        raise HTTPException(status_code=400, detail='El producto ya existe')

    return await crud.create(new_obj, session)


@router.get("/", response_model=list[schema.Products])
async def get_obj_all(session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    return await crud.read_all_limit(session, offset, limit)


@router.get('/key/{key}', response_model=schema.Products)
async def get_obj_by_key(key: int, session: SessionDep):

    existing_obj = await crud.read_by_key(key, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id_odoo del producto no existe')

    return existing_obj


@router.get('/id/{id}', response_model=schema.Products)
async def get_obj_by_id(id: int, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del producto no existe')

    return existing_obj


@router.patch("/id/{id}/{values}", response_model=schema.Products)
async def patch_obj(id: int, obj_new_vals: schema.ProductsUpdate, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del producto no existe')

    return await crud.update(existing_obj, obj_new_vals, session)


@router.delete("/id/{id}", response_model=str)
async def delete_obj(id: int, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del producto no existe')

    return await crud.delete(existing_obj, session)
