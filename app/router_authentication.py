from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from . import schema, crud_authentication

from .orm import get_db



router = APIRouter(
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)



@router.post("/users")
async def create_user(schema: schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = await crud_authentication.get_user(schema.user, db)

    if existing_user:
        raise HTTPException(status_code=400, detail='El usuario ya existe')
    
    user_obj = await crud_authentication.create_user(schema, db)

    return await crud_authentication.create_token(user_obj)



@router.post("/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_authenticated = await crud_authentication.authenticate_user(form_data.username, form_data.password, db)

    if not user_authenticated:
        raise HTTPException(status_code=401, detail="Usuario y/o Contraseña inválidos")

    return await crud_authentication.create_token(user_authenticated)



@router.get("/users/me", response_model= schema.User)
async def read_users_me(current_user: schema.User = Depends(crud_authentication.get_current_user)):

    return current_user