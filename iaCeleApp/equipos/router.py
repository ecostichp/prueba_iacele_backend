# Se importan las librerías necesarias
from fastapi import APIRouter, HTTPException, Query
from typing import Annotated

from . import schema, crud
from ..database import SessionDep
from ..authentication import authentication_require


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
    # dependencies=[authentication_require]
)


@router.post("/new", response_model=schema.Teams)
async def post_obj(new_obj: schema.TeamsCreate, session: SessionDep):

    existing_obj = await crud.read_by_employees(new_obj.empleado_id_a, new_obj.empleado_id_b, session)

    if existing_obj:
        raise HTTPException(status_code=400, detail='Uno de los empleados ya tiene equipo')

    return await crud.create(new_obj, session)


@router.get("/", response_model=list[schema.Teams])
async def get_obj_all(session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    return await crud.read_all_limit(session, offset, limit)


@router.patch("/id/{id}/{values}", response_model=schema.Teams)
async def patch_obj(id: int, obj_new_vals: schema.TeamsUpdate, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del equipo no existe')

    return await crud.update(existing_obj, obj_new_vals, session)


@router.delete("/id/{id}", response_model=str)
async def delete_obj(id: int, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del equipo no existe')

    return await crud.delete(existing_obj, session)
