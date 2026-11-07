from sqlalchemy import and_, delete as delete_rows, update
from sqlmodel  import Session, select, func, case, alias

from ..timeutil import as_utc
from . import schema
from ..productos import schema as schema_productos
from ..equipos import schema as schema_equipos

def read_all_limit(session: Session, offset: int, limit: int|None):

    statement = select(schema.Inventory).offset(offset).limit(limit)
    all = session.exec(statement).all()

    return all


def read_by_key(key: int, session: Session):

    statement = select(schema.Inventory).where(schema.Inventory.id_products == key)

    return session.exec(statement).first()


def read_by_id(id: int, session: Session):

    return session.get(schema.Inventory, id)


def _register_dict(inventory: schema.Inventory) -> dict:
    data = dict(inventory)
    created = as_utc(data.get("date_create"))
    data["date_create"] = None if created is None else created.isoformat()
    return data


def create(new_obj: schema.InventoryCreate, session: Session):
    
    db_obj = schema.Inventory.model_validate(new_obj)
    db_obj.date_create = as_utc(db_obj.date_create)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def find_stage_register(new_obj: schema.InventoryCreate, session: Session):
    if new_obj.count_type == schema.TipoConteo.individual:
        return None

    statement = (
        select(schema.Inventory)
        .where(schema.Inventory.id_products == new_obj.id_products)
        .where(schema.Inventory.count_type == new_obj.count_type)
    )
    if new_obj.count_type == schema.TipoConteo.equipo:
        statement = statement.where(schema.Inventory.assigned_team_id == new_obj.assigned_team_id)
    else:
        statement = statement.where(schema.Inventory.counting_user_id == new_obj.counting_user_id)
    return session.exec(statement).first()


def delete(existing_obj:schema.Inventory, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Producto borrado con éxito'


def get_inventory_stage(session: Session) -> schema.InventoryStage:
    row = session.get(schema.InventoryStage, 1)
    if row:
        return row

    row = schema.InventoryStage(id=1, stage=schema.TipoConteo.individual)
    session.add(row)
    try:
        session.commit()
    except Exception:
        session.rollback()
        row = session.get(schema.InventoryStage, 1)
        if row:
            return row
        raise
    session.refresh(row)
    return row


def set_inventory_stage(stage: schema.TipoConteo, session: Session) -> schema.InventoryStage:
    row = get_inventory_stage(session)
    row.stage = stage
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def assign_counts_to_counters(session: Session) -> None:
    individual = schema.Inventory.count_type == schema.TipoConteo.individual
    session.exec(
        update(schema.Inventory)
        .where(individual)
        .where(schema.Inventory.assigned_user_id != schema.Inventory.counting_user_id)
        .values(assigned_user_id=schema.Inventory.counting_user_id)
    )
    teams = session.exec(select(schema_equipos.Teams)).all()
    for team in teams:
        for member in (team.empleado_id_a, team.empleado_id_b):
            if not member:
                continue
            session.exec(
                update(schema.Inventory)
                .where(individual)
                .where(schema.Inventory.counting_user_id == member)
                .values(assigned_user_id=member, assigned_team_id=team.id)
            )
    session.exec(
        update(schema.Inventory)
        .where(schema.Inventory.count_type != schema.TipoConteo.individual)
        .values(assigned_user_id=None)
    )


def delete_all(session: Session):
    result = session.exec(delete_rows(schema.Inventory))
    deleted = int(result.rowcount or 0)
    session.commit()
    return deleted


def read_invidual_code_registers_all(
    employee_id: int,
    id_product: int,
    session: Session,
    by_counting: bool = False,
    count_type: schema.TipoConteo | None = None,
):

    kind = count_type or get_inventory_stage(session).stage
    owner = schema.Inventory.assigned_user_id if not by_counting else schema.Inventory.counting_user_id
    statement = (
            select(
                schema.Inventory,
                schema_productos.Products.id,
                schema_productos.Products.code,
                schema_productos.Products.name,
            )
            .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
            .where(owner == employee_id)
            .where(schema.Inventory.assigned_user_id == schema.Inventory.counting_user_id)
            .where(schema.Inventory.count_type == kind)
            .where(schema.Inventory.id_products == id_product)
        )

    all_registers = session.exec(statement).all()

    if not all_registers:
        product = session.get(schema_productos.Products, id_product)
        return [
            {
                "product_id": {
                    "id": product.id if product else id_product,
                    "code": product.code if product else "",
                    "name": product.name if product else "",
                    "total_qty": 0,
                },
                "registers": [],
            }
        ]
    
    return [
        {
            "product_id": {
                "id": all_registers[0]._mapping["id"],
                "code": all_registers[0]._mapping["code"],
                "name": all_registers[0]._mapping["name"],
                "total_qty": sum(
                    reg._mapping["Inventory"].count_qty for reg in all_registers 
                    if reg._mapping["Inventory"].count_qty is not None
                ),
            },
            "registers": [_register_dict(row._mapping["Inventory"]) for row in all_registers]
        }
    ]


def read_invidual_registers_limit(employee_id: int, session: Session, offset: int, limit: int|None):

    stage = get_inventory_stage(session).stage
    statement = (
            select(
                schema.Inventory.id_products,
                schema_productos.Products.code,
                schema_productos.Products.name,
                func.sum(schema.Inventory.count_qty).label("total_qty"),
                func.max(schema.Inventory.date_create).label("last_count"),
            )
            .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
            .where(schema.Inventory.assigned_user_id == employee_id)
            .where(schema.Inventory.assigned_user_id == schema.Inventory.counting_user_id)
            .where(schema.Inventory.count_type == stage)
            .group_by(
                schema.Inventory.id_products,
                schema_productos.Products.code,
                schema_productos.Products.name
            )
            .offset(offset)
            .limit(limit)
        )

    all_registers = session.exec(statement).all()

    return [dict(row._mapping) for row in all_registers]


def read_team_registers_limit(team: schema_equipos.Teams, session: Session, offset: int, limit: int|None):
        
    empleado_id_a = team.empleado_id_a
    empleado_id_b = team.empleado_id_b

    # 2. Definimos la estructura base de la consulta para el Empleado 1 (stmt1)
    stmt1 = (
        select(
            schema.Inventory.id_products,
            schema_productos.Products.code.label("code_a"),
            schema_productos.Products.name.label("name_a"),
            func.sum(schema.Inventory.count_qty).label("total_qty_a")
        )
        .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
        .where(schema.Inventory.assigned_user_id == empleado_id_a)
        .where(schema.Inventory.assigned_user_id == schema.Inventory.counting_user_id)
        .where(schema.Inventory.assigned_team_id == team.id)
        .where(schema.Inventory.count_type == schema.TipoConteo.individual)
        .group_by(
            schema.Inventory.id_products, 
            schema_productos.Products.code, 
            schema_productos.Products.name
        )
    ).subquery()

    # 3. Definimos la estructura base de la consulta para el Empleado 2 (stmt2)
    stmt2 = (
        select(
            schema.Inventory.id_products,
            schema_productos.Products.code.label("code_b"),
            schema_productos.Products.name.label("name_b"),
            func.sum(schema.Inventory.count_qty).label("total_qty_b")
        )
        .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
        .where(schema.Inventory.assigned_user_id == empleado_id_b)
        .where(schema.Inventory.assigned_user_id == schema.Inventory.counting_user_id)
        .where(schema.Inventory.assigned_team_id == team.id)
        .where(schema.Inventory.count_type == schema.TipoConteo.individual)
        .group_by(
            schema.Inventory.id_products, 
            schema_productos.Products.code, 
            schema_productos.Products.name
        )
    ).subquery()

    stmt_equipo = (
        select(
            schema.Inventory.id_products,
            func.sum(schema.Inventory.count_qty).label("total_qty_equipo"),
        )
        .where(schema.Inventory.assigned_team_id == team.id)
        .where(schema.Inventory.count_type == schema.TipoConteo.equipo)
        .group_by(schema.Inventory.id_products)
    ).subquery()

    # 4. Realizamos el FULL OUTER JOIN combinando ambas subconsultas por 'id_products'
    compared = (
        select(
            func.coalesce(stmt1.c.id_products, stmt2.c.id_products).label("id_products"),
            func.coalesce(stmt1.c.code_a, stmt2.c.code_b).label("code"),
            func.coalesce(stmt1.c.name_a, stmt2.c.name_b).label("name"),
            stmt1.c.total_qty_a,
            stmt2.c.total_qty_b,
            case(
                (
                    and_(
                        stmt1.c.total_qty_a.is_not(None),
                        stmt2.c.total_qty_b.is_not(None),
                        stmt1.c.total_qty_a == stmt2.c.total_qty_b,
                    ),
                    True,
                ),
                else_=False,
            ).label("iguales")
        )
        .join(stmt2, stmt1.c.id_products == stmt2.c.id_products, full=True)
    ).subquery()

    statement = (
        select(
            compared.c.id_products,
            compared.c.code,
            compared.c.name,
            compared.c.total_qty_a,
            compared.c.total_qty_b,
            compared.c.iguales,
            stmt_equipo.c.total_qty_equipo,
        )
        .outerjoin(stmt_equipo, compared.c.id_products == stmt_equipo.c.id_products)
        .order_by(compared.c.name)
        .offset(offset)
        .limit(limit)
    )

    all_registers = session.exec(statement).all()

    return [dict(row._mapping) for row in all_registers]


def read_team_product_registers(team_id: int, id_product: int, session: Session):
    statement = (
        select(
            schema.Inventory,
            schema_productos.Products.id,
            schema_productos.Products.code,
            schema_productos.Products.name,
        )
        .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
        .where(schema.Inventory.assigned_team_id == team_id)
        .where(schema.Inventory.id_products == id_product)
        .where(schema.Inventory.count_type == schema.TipoConteo.equipo)
    )
    rows = session.exec(statement).all()
    product = session.get(schema_productos.Products, id_product)
    registers = [_register_dict(row._mapping["Inventory"]) for row in rows]
    registers.sort(key=lambda item: item.get("date_create") or "", reverse=True)
    return [
        {
            "product_id": {
                "id": product.id if product else id_product,
                "code": product.code if product else "",
                "name": product.name if product else "",
                "total_qty": sum((item.get("count_qty") or 0) for item in registers),
            },
            "registers": registers,
        }
    ]
