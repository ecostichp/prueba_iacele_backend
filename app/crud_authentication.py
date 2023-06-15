from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from jwt import encode, decode
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer

from . import model, schema
from .orm import get_db



JWT_SECRET = "myjwtsecret"

oauth2schema = OAuth2PasswordBearer(tokenUrl="/token")


async def get_user(user:str, db: Session):
    return db.query(model.User).filter(model.User.user == user).first()



async def create_user(schema:schema.UserCreate, db: Session):
    user_obj = model.User(
        user = schema.user,
        name = schema.name,
        position = schema.position,
        avatar = schema.avatar,
        hashed_password = bcrypt.hash(schema.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj



async def create_token(model: model.User):
    user_obj_schema = schema.User.from_orm(model)

    token = encode(user_obj_schema.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")



async def authenticate_user(user:str, password:str, db: Session):
    user_authenticated = await get_user(user, db)
    
    if user_authenticated and user_authenticated.verify_password(password):
        return user_authenticated
    
    return False



async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2schema),
):
    try:
        payload = decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(model.User).get(payload["id"])
    except:
        raise HTTPException(
            status_code=401, detail="Usuario y/o Contraseña inválidas"
        )

    return schema.User.from_orm(user)