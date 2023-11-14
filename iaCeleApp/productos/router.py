# Se importan las librerías necesarias
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


from . import crud, schema

from ..database import get_db


# Se instancía la clase para generar el objeto 'router'
router = APIRouter(
    prefix="/productos",
    tags=["productos"],
    responses={404: {"description": "Not found"}},
)



# Se contruyen todas las rutas y debajo de ellas el end-point
@router.get("/", response_model=List[schema.Productos])
async def get_all_productos(db: Session = Depends(get_db)):

    return await crud.get_all_products(db)


@router.get('/codigo/{product_code}', response_model=schema.Productos)
async def get_product_by_code(product_code: int, db: Session = Depends(get_db)):

    existing_product = await crud.get_product_by_codigo(db, product_code)

    if not existing_product:
        raise HTTPException(status_code=400, detail='El producto no existe')

    return existing_product


@router.get('/id/{product_id}', response_model=schema.Productos)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):

    existing_product = await crud.get_product_by_id(db, product_id)

    if not existing_product:
        raise HTTPException(status_code=400, detail='El id no existe')

    return existing_product


@router.post("/new", response_model=schema.Productos)
async def create_product(schema: schema.ProductosCreate, db: Session = Depends(get_db)):

    existing_product = await crud.get_product_by_codigo(db, schema.codigo)

    if existing_product:
        raise HTTPException(status_code=400, detail='El producto ya existe')

    return await crud.create_product(db, schema)


@router.delete("/codigo/{product_code}", response_model=str)
async def delete_product(product_code: int, db: Session = Depends(get_db)):

    existing_product = await crud.get_product_by_codigo(db, product_code)

    if not existing_product:
        raise HTTPException(status_code=400, detail='El producto no existe')

    return await crud.delete_product(db, existing_product)


@router.patch("/codigo/{product_code}/{values}", response_model=str)
async def update_product(product_code: int, values: str, db: Session = Depends(get_db)):

    existing_product = await crud.get_product_by_codigo(db, product_code)

    if not existing_product:
        raise HTTPException(status_code=400, detail='El producto no existe')

    return await crud.update_product(db, values, existing_product)
