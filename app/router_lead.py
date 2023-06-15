from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from . import schema, crud_lead, crud_authentication

from .orm import get_db



router = APIRouter(
    tags=["lead"],
    responses={404: {"description": "Not found"}},
)



@router.post("/leads")
async def create_lead(
    schema: schema.LeadCreate, 
    db: Session = Depends(get_db), 
    current_user: schema.User = Depends(crud_authentication.get_current_user)
    ):

    return await crud_lead.create_lead(schema, db, current_user)



@router.get("/leads", response_model=List[schema.Lead])
async def get_leads(
    db: Session = Depends(get_db), 
    current_user: schema.User = Depends(crud_authentication.get_current_user)
    ):

    return await crud_lead.get_leads_all(db, current_user)



@router.get("/leads/{lead_id}", status_code=200)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db), 
    current_user: schema.User = Depends(crud_authentication.get_current_user)
    ):

    return await crud_lead.get_lead_by_id(lead_id, db, current_user)



@router.delete("/leads/{lead_id}", status_code=200)
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db), 
    current_user: schema.User = Depends(crud_authentication.get_current_user)
    ):

    return await crud_lead.delete_lead_by_id(lead_id, db, current_user)



@router.put("/leads/{lead_id}", status_code=200)
async def update_lead(
    lead_id: int,
    lead_new_values: schema.LeadCreate,
    db: Session = Depends(get_db), 
    current_user: schema.User = Depends(crud_authentication.get_current_user)
    ):

    return await crud_lead.update_lead_by_id(lead_id, lead_new_values, db, current_user)