from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from . import model, schema



async def create_lead(_schema:schema.LeadCreate, db: Session, current_user: schema.User):
    lead_obj = model.Lead(**_schema.dict(), owner_id = current_user.id)
    db.add(lead_obj)
    db.commit()
    db.refresh(lead_obj)

    return schema.Lead.from_orm(lead_obj)



async def get_leads_all(db: Session, current_user: schema.User):
    leads = db.query(model.Lead).filter_by(owner_id = current_user.id)

    return list(map(schema.Lead.from_orm, leads))



async def lead_selector_by_id(lead_id: int, db: Session, current_user: schema.User):
    lead = (db.query(model.Lead)
            .filter_by(owner_id=current_user.id)
            .filter(model.Lead.id == lead_id)
            .first()
    )

    if lead is None:
        raise HTTPException(status_code=404, detail="El Lead no existe")
    
    return lead



async def get_lead_by_id(lead_id: int, db: Session, current_user: schema.User):
    lead_selected = await lead_selector_by_id(lead_id, db, current_user)
    
    return schema.Lead.from_orm(lead_selected)



async def delete_lead_by_id(lead_id: int, db: Session, current_user: schema.User):
    lead_selected = await lead_selector_by_id(lead_id, db, current_user)
    
    db.delete(lead_selected)
    db.commit()

    return {"message", "Successfully Deleted"}



async def update_lead_by_id(lead_id: int, lead_new_values: schema.LeadCreate, db: Session, current_user: schema.User):
    lead_selected = await lead_selector_by_id(lead_id, db, current_user)

    lead_selected.first_name = lead_new_values.first_name
    lead_selected.last_name = lead_new_values.last_name
    lead_selected.email = lead_new_values.email
    lead_selected.company = lead_new_values.company
    lead_selected.note = lead_new_values.note
    lead_selected.date_last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(lead_selected)

    return schema.Lead.from_orm(lead_selected)