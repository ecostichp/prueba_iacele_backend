# Se importan las librerías necesarias
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from . import schema, crud
from ..database import SessionDep
from ..authentication import authentication_require
from ..authentication.crud import require_user_authenticated
from ..authentication.schema import Authentications
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
def post_obj(new_obj: schema.InventoryCreate, session: SessionDep):

    return crud.create(new_obj, session)


@router.get("/registers", response_model=list[schema.Inventory])
def get_obj_all(session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    return crud.read_all_limit(session, offset, limit)


@router.get("/individuals/id/{id_employee}", response_model=list[schema.Inventory_InvididualRegisters])
def get_obj_by_id(id_employee: int, session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    existing_obj = crud_empleados.read_by_id(id_employee, session)
    
    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del empleado no existe')
    
    return crud.read_invidual_registers_limit(id_employee, session, offset, limit)


@router.get("/individuals/id/{id_employee}/product/{id_product}", response_model=list[schema.Inventory_InvididualProductAllRegisters])
def get_obj_by_id(id_employee: int, id_product:int, session: SessionDep):

    existing_obj_employee = crud_empleados.read_by_id(id_employee, session)
    
    if not existing_obj_employee:
        raise HTTPException(status_code=400, detail='El id del empleado no existe')

    existing_obj_prod = crud_productos.read_by_id(id_product, session)
        
    if not existing_obj_prod:
        raise HTTPException(status_code=400, detail='El id del producto no existe')
    
    return crud.read_invidual_code_registers_all(id_employee, id_product, session)


@router.get("/teams/id/{id_team}", response_model=list[schema.Inventory_TeamRegisters])
def get_obj_by__team(id_team: int, session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    existing_obj = crud_equipos.read_by_id(id_team, session)
    
    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del equipo no existe')
    
    return crud.read_team_registers_limit(existing_obj, session, offset, limit)


@router.delete("/registers")
def delete_all_registers(
    session: SessionDep,
    current_user: Annotated[Authentications, Depends(require_user_authenticated)],
):
    employee = None
    if current_user.empleado_id:
        employee = crud_empleados.read_by_id(current_user.empleado_id, session)
    title = (employee.job_title if employee else "").strip().casefold()
    if title != "director general":
        raise HTTPException(status_code=403, detail="No puedes borrar el inventario")

    deleted = crud.delete_all(session)
    return {"deleted": deleted}


@router.delete("/id/{id}", response_model=str)
def delete_obj(id: int, session: SessionDep):

    existing_obj = crud.read_by_id(id, session)

    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del conteo individual no existe')

    return crud.delete(existing_obj, session)
