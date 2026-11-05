# Se importan las librerías necesarias
from fastapi import APIRouter, HTTPException, Query
from typing import Annotated

from . import schema, crud
from ..database import SessionDep
from ..authentication import authentication_require
from ..empleados import crud as crud_empleados
from ..equipos import crud as crud_equipos
from ..productos import crud as crud_productos


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
    # dependencies=[authentication_require]
)



@router.post("/registers/new", response_model=schema.Inventory)
async def post_obj(new_obj: schema.InventoryCreate, session: SessionDep):

    return await crud.create(new_obj, session)


@router.get("/registers", response_model=list[schema.Inventory])
async def get_obj_all(session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    return await crud.read_all_limit(session, offset, limit)


@router.get("/individuals/id/{id_employee}", response_model=list[schema.Inventory_InvididualRegisters])
async def get_obj_by_id(id_employee: int, session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    existing_obj = await crud_empleados.read_by_id(id_employee, session)
    
    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del empleado no existe')
    
    return await crud.read_invidual_registers_limit(id_employee, session, offset, limit)


@router.get("/individuals/id/{id_employee}/product/{id_product}", response_model=list[schema.Inventory_InvididualProductAllRegisters])
async def get_obj_by_id(id_employee: int, id_product:int, session: SessionDep):

    existing_obj_employee = await crud_empleados.read_by_id(id_employee, session)
    
    if not existing_obj_employee:
        raise HTTPException(status_code=400, detail='El id del empleado no existe')

    existing_obj_prod = await crud_productos.read_by_id(id_product, session)
        
    if not existing_obj_prod:
        raise HTTPException(status_code=400, detail='El id del producto no existe')
    
    return await crud.read_invidual_code_registers_all(id_employee, id_product, session)


@router.get("/teams/id/{id_team}", response_model=list[schema.Inventory_TeamRegisters])
async def get_obj_by__team(id_team: int, session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    existing_obj = await crud_equipos.read_by_id(id_team, session)
    
    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del equipo no existe')
    
    return await crud.read_team_registers_limit(existing_obj, session, offset, limit)


@router.delete("/id/{id}", response_model=str)
async def delete_obj(id: int, session: SessionDep):

    existing_obj = await crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del conteo individual no existe')

    return await crud.delete(existing_obj, session)
