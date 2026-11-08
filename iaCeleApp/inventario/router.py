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



def stamp_count_owners(new_obj: schema.InventoryCreate, session: SessionDep) -> schema.InventoryCreate:
    from ..authentication.crud import read_by_employee_id

    account = read_by_employee_id(new_obj.counting_user_id, session)
    if not account or not account.empleado_id:
        raise HTTPException(status_code=400, detail="Quien cuenta no tiene usuario")

    stage = crud.get_inventory_stage(session).stage
    counter_id = account.empleado_id
    if stage == schema.TipoConteo.individual:
        assigned_id = account.assigned_user_id or counter_id
        team_member = assigned_id
    else:
        assigned_id = None
        team_member = counter_id
    team = crud_equipos.read_by_member(team_member, session)
    if not team or not team.id:
        raise HTTPException(
            status_code=400,
            detail="La persona a la que se asigna el conteo no tiene equipo",
        )

    return new_obj.model_copy(update={
        "counting_user_id": account.empleado_id,
        "assigned_user_id": assigned_id,
        "assigned_team_id": team.id,
        "count_type": crud.get_inventory_stage(session).stage,
    })


@router.get("/stage", response_model=schema.InventoryStagePublic)
def read_stage(session: SessionDep):
    row = crud.get_inventory_stage(session)
    return schema.InventoryStagePublic(stage=row.stage)


@router.put("/stage", response_model=schema.InventoryStagePublic)
def update_stage(
    body: schema.InventoryStagePublic,
    session: SessionDep,
    current_user: Annotated[Authentications, Depends(require_user_authenticated)],
):
    from ..authentication.crud import is_director_general, restore_original_assignments

    if not is_director_general(current_user, session):
        raise HTTPException(status_code=403, detail="No puedes cambiar la etapa del inventario")

    current = crud.get_inventory_stage(session)
    if current.stage == schema.TipoConteo.individual and body.stage != schema.TipoConteo.individual:
        restore_original_assignments(session)
        crud.assign_counts_to_counters(session)

    row = crud.set_inventory_stage(body.stage, session)
    return schema.InventoryStagePublic(stage=row.stage)


@router.post("/registers/new", response_model=schema.Inventory)
def post_obj(new_obj: schema.InventoryCreate, session: SessionDep):

    stamped = stamp_count_owners(new_obj, session)
    if stamped.count_qty < 0 or (
        stamped.count_type == schema.TipoConteo.individual and stamped.count_qty == 0
    ):
        detail = (
            "En la etapa individual no se guarda cero. Borra el registro."
            if stamped.count_type == schema.TipoConteo.individual
            else "La cantidad no puede ser negativa."
        )
        raise HTTPException(status_code=400, detail=detail)
    if crud.find_stage_register(stamped, session):
        raise HTTPException(
            status_code=409,
            detail="En esta etapa solo se permite un registro por código.",
        )
    return crud.create(stamped, session)


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
def get_obj_by_id(
    id_employee: int,
    id_product: int,
    session: SessionDep,
    owner: str = Query("assigned"),
    count_type: schema.TipoConteo | None = None,
):

    existing_obj_employee = crud_empleados.read_by_id(id_employee, session)
    
    if not existing_obj_employee:
        raise HTTPException(status_code=400, detail='El id del empleado no existe')

    existing_obj_prod = crud_productos.read_by_id(id_product, session)
        
    if not existing_obj_prod:
        raise HTTPException(status_code=400, detail='El id del producto no existe')
    
    return crud.read_invidual_code_registers_all(
        id_employee,
        id_product,
        session,
        by_counting=owner == "counting",
        count_type=count_type,
    )


@router.get("/two-counts", response_model=list[schema.InventoryTwoCount])
def get_codes_with_two_counts(session: SessionDep):
    return crud.read_codes_with_two_counts(session)


@router.get("/teams/id/{id_team}", response_model=list[schema.Inventory_TeamRegisters])
def get_obj_by__team(id_team: int, session: SessionDep, offset: int = 0, limit:Annotated[int|None, Query(le=100)] = None):

    existing_obj = crud_equipos.read_by_id(id_team, session)
    
    if not existing_obj:
        raise HTTPException(status_code=400, detail='El id del equipo no existe')
    
    return crud.read_team_registers_limit(existing_obj, session, offset, limit)


@router.get("/teams/id/{id_team}/product/{id_product}", response_model=list[schema.Inventory_InvididualProductAllRegisters])
def get_team_product(id_team: int, id_product: int, session: SessionDep):
    existing_obj = crud_equipos.read_by_id(id_team, session)
    if not existing_obj:
        raise HTTPException(status_code=400, detail="El id del equipo no existe")
    if not crud_productos.read_by_id(id_product, session):
        raise HTTPException(status_code=400, detail="El id del producto no existe")
    return crud.read_team_product_registers(id_team, id_product, session)


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

    stage = crud.get_inventory_stage(session).stage
    if existing_obj.count_type == schema.TipoConteo.individual and stage != schema.TipoConteo.individual:
        raise HTTPException(status_code=403, detail="No se pueden borrar los conteos de la etapa individual.")

    return crud.delete(existing_obj, session)
