from sqlalchemy import and_, delete as delete_rows, or_, update
from sqlmodel  import Session, select, func, case

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
        .where(schema.same_count_type(schema.Inventory.count_type, new_obj.count_type))
    )
    if new_obj.count_type == schema.TipoConteo.diferencias:
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
    session.exec(
        update(schema.Inventory)
        .where(schema.Inventory.count_type != schema.TipoConteo.individual)
        .values(assigned_user_id=None)
    )


def repair_help_assignments(session: Session) -> int:
    from ..authentication.schema import AssignmentNotice, DataRepair
    from ..database.config import settings

    if settings.db_mode.strip().lower() == "sqlite":
        return 0

    repair_id = "help-assignments-v1"
    if session.get(DataRepair, repair_id):
        print(f"REPAIR {repair_id} ya estaba aplicado")
        return 0

    notices = session.exec(select(AssignmentNotice)).all()
    teams = session.exec(select(schema_equipos.Teams)).all()
    team_by_member = {}
    for team in teams:
        if team.id is None:
            continue
        if team.empleado_id_a:
            team_by_member[team.empleado_id_a] = team.id
        if team.empleado_id_b:
            team_by_member[team.empleado_id_b] = team.id

    by_helper = {}
    for notice in notices:
        if notice.empleado_id is None or notice.fecha_alta is None:
            continue
        by_helper.setdefault(notice.empleado_id, []).append(notice)

    windows = []
    for helper_id, items in by_helper.items():
        items.sort(key=lambda notice: (as_utc(notice.fecha_alta), notice.id or 0))
        for index, notice in enumerate(items):
            if notice.assigned_user_id == helper_id:
                continue
            start = as_utc(notice.fecha_alta)
            end = as_utc(items[index + 1].fecha_alta) if index + 1 < len(items) else None
            windows.append((
                helper_id,
                start,
                end,
                notice.assigned_user_id,
                team_by_member.get(notice.assigned_user_id),
            ))

    changed = 0
    if windows:
        helper_ids = list({window[0] for window in windows})
        rows = session.exec(
            select(schema.Inventory)
            .where(schema.Inventory.count_type == schema.TipoConteo.individual)
            .where(schema.Inventory.counting_user_id.in_(helper_ids))
        ).all()
        for row in rows:
            created = as_utc(row.date_create)
            if created is None:
                continue
            match = None
            for helper_id, start, end, target_id, team_id in windows:
                if row.counting_user_id != helper_id or created < start:
                    continue
                if end is not None and created >= end:
                    continue
                match = (target_id, team_id)
                break
            if match is None:
                continue
            target_id, team_id = match
            same_user = row.assigned_user_id == target_id
            same_team = team_id is None or row.assigned_team_id == team_id
            if same_user and same_team:
                continue
            print(
                f"REPAIR inventory {row.id} assigned {row.assigned_user_id} -> {target_id}"
                f" team {row.assigned_team_id} -> {team_id if team_id is not None else row.assigned_team_id}"
            )
            row.assigned_user_id = target_id
            if team_id is not None:
                row.assigned_team_id = team_id
            session.add(row)
            changed += 1

    session.add(DataRepair(id=repair_id))
    try:
        session.commit()
    except Exception as error:
        session.rollback()
        if session.get(DataRepair, repair_id):
            print(f"REPAIR {repair_id} ya estaba aplicado")
            return 0
        raise error
    print(f"REPAIR {repair_id} updated={changed}")
    return changed


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
            .where(schema.same_count_type(schema.Inventory.count_type, kind))
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
            .where(schema.same_count_type(schema.Inventory.count_type, stage))
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

    # Todo lo asignado a cada persona, aunque lo haya contado alguien más.
    # El equipo solo indica a quiénes se compara.
    propios = (
        select(
            schema.Inventory.id_products,
            schema.Inventory.assigned_user_id,
            schema.Inventory.count_qty,
        )
        .where(schema.Inventory.count_type == schema.TipoConteo.individual)
    ).subquery()

    stmt1 = (
        select(
            propios.c.id_products,
            schema_productos.Products.code.label("code_a"),
            schema_productos.Products.name.label("name_a"),
            func.sum(propios.c.count_qty).label("total_qty_a"),
        )
        .join(schema_productos.Products, propios.c.id_products == schema_productos.Products.id)
        .where(propios.c.assigned_user_id == empleado_id_a)
        .group_by(
            propios.c.id_products,
            schema_productos.Products.code,
            schema_productos.Products.name,
        )
    ).subquery()

    stmt2 = (
        select(
            propios.c.id_products,
            schema_productos.Products.code.label("code_b"),
            schema_productos.Products.name.label("name_b"),
            func.sum(propios.c.count_qty).label("total_qty_b"),
        )
        .join(schema_productos.Products, propios.c.id_products == schema_productos.Products.id)
        .where(propios.c.assigned_user_id == empleado_id_b)
        .group_by(
            propios.c.id_products,
            schema_productos.Products.code,
            schema_productos.Products.name,
        )
    ).subquery()

    stmt_equipo = (
        select(
            schema.Inventory.id_products,
            func.sum(schema.Inventory.count_qty).label("total_qty_equipo"),
        )
        .where(schema.Inventory.assigned_team_id == team.id)
        .where(schema.same_count_type(schema.Inventory.count_type, schema.TipoConteo.diferencias))
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


def read_codes_with_two_counts(session: Session):
    individual = (
        select(
            schema.Inventory.assigned_user_id.label("assigned_user_id"),
            schema.Inventory.id_products.label("id_products"),
            func.sum(schema.Inventory.count_qty).label("total_qty"),
        )
        .where(schema.Inventory.count_type == schema.TipoConteo.individual)
        .group_by(schema.Inventory.assigned_user_id, schema.Inventory.id_products)
        .subquery()
    )

    ranked = (
        select(
            schema.Inventory.assigned_team_id.label("assigned_team_id"),
            schema.Inventory.id_products.label("id_products"),
            schema.Inventory.count_qty.label("count_qty"),
            func.row_number().over(
                partition_by=(schema.Inventory.assigned_team_id, schema.Inventory.id_products),
                order_by=schema.Inventory.id.desc(),
            ).label("rn"),
        )
        .where(schema.same_count_type(schema.Inventory.count_type, schema.TipoConteo.diferencias))
        .subquery()
    )
    diferencias = (
        select(
            ranked.c.assigned_team_id,
            ranked.c.id_products,
            ranked.c.count_qty,
        )
        .where(ranked.c.rn == 1)
        .subquery()
    )

    teams = schema_equipos.Teams
    side_a = (
        select(
            teams.id.label("team_id"),
            individual.c.id_products,
            individual.c.total_qty.label("qty_a"),
        )
        .join(individual, individual.c.assigned_user_id == teams.empleado_id_a)
        .subquery()
    )
    side_b = (
        select(
            teams.id.label("team_id"),
            individual.c.id_products,
            individual.c.total_qty.label("qty_b"),
        )
        .join(individual, individual.c.assigned_user_id == teams.empleado_id_b)
        .subquery()
    )
    compared = (
        select(
            func.coalesce(side_a.c.team_id, side_b.c.team_id).label("team_id"),
            func.coalesce(side_a.c.id_products, side_b.c.id_products).label("id_products"),
            side_a.c.qty_a,
            side_b.c.qty_b,
        )
        .join(
            side_b,
            and_(
                side_a.c.team_id == side_b.c.team_id,
                side_a.c.id_products == side_b.c.id_products,
            ),
            full=True,
        )
        .subquery()
    )

    matched = and_(
        compared.c.qty_a.is_not(None),
        compared.c.qty_b.is_not(None),
        compared.c.qty_a == compared.c.qty_b,
    )
    has_individual = or_(compared.c.qty_a.is_not(None), compared.c.qty_b.is_not(None))
    take_difference = and_(has_individual, ~matched, diferencias.c.count_qty.is_not(None))

    # tabla1: iguales. Un registro individual por equipo y código.
    # tabla2: no iguales, solo si ya existe el conteo de diferencias que los corrige.
    records = (
        select(
            schema_productos.Products.id.label("id_products"),
            schema_productos.Products.code,
            schema_productos.Products.name,
            case((matched, "individual"), else_="diferencias").label("tipo"),
        )
        .select_from(compared)
        .join(schema_productos.Products, schema_productos.Products.id == compared.c.id_products)
        .outerjoin(
            diferencias,
            and_(
                diferencias.c.assigned_team_id == compared.c.team_id,
                diferencias.c.id_products == compared.c.id_products,
            ),
        )
        .where(or_(matched, take_difference))
    ).subquery()

    registros = func.count()
    individuales = func.sum(case((records.c.tipo == "individual", 1), else_=0))
    de_diferencias = func.sum(case((records.c.tipo == "diferencias", 1), else_=0))
    statement = (
        select(
            records.c.id_products,
            records.c.code,
            records.c.name,
            registros.label("registros"),
            individuales.label("individuales"),
            de_diferencias.label("diferencias"),
            (registros > 1).label("dobles"),
        )
        .group_by(records.c.id_products, records.c.code, records.c.name)
        .having(registros > 1)
        .order_by(records.c.code)
    )
    rows = session.exec(statement).all()
    return [
        {
            "id_products": row.id_products,
            "code": row.code,
            "name": row.name,
            "registros": int(row.registros or 0),
            "individuales": int(row.individuales or 0),
            "diferencias": int(row.diferencias or 0),
            "dobles": bool(row.dobles),
        }
        for row in rows
    ]


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
        .where(schema.same_count_type(schema.Inventory.count_type, schema.TipoConteo.diferencias))
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
