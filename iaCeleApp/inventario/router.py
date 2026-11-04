# Se importan las librerías necesarias
from fastapi import APIRouter, HTTPException, Query
from typing import Annotated

from . import schema, crud
from ..database import SessionDep
from ..authentication import authentication_require


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
    # dependencies=[authentication_require]
)


@router.post("/individuals/new", response_model=schema.Inventory_individual)
async def post_obj(new_obj: schema.Inventory_individualCreate, session: SessionDep):

    return await crud.create(new_obj, session)


@router.get("/individuals", response_model=list[schema.Inventory_individual])
async def get_obj_all(session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    return await crud.read_all_limit(session, offset, limit)


@router.patch("/id/{id}/{values}", response_model=schema.Inventory_individual)
async def patch_obj(id: int, obj_new_vals: schema.Inventory_individualUpdate, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del conteo individual no existe')

    return await crud.update(existing_obj, obj_new_vals, session)


@router.delete("/id/{id}", response_model=str)
async def delete_obj(id: int, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del conteo individual no existe')

    return await crud.delete(existing_obj, session)
