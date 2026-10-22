from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from jwt import encode, decode
from pwdlib import PasswordHash 
from fastapi.security import OAuth2PasswordBearer

from . import model, schema
from ..database import get_db


JWT_SECRET = "myjwtsecret"

# Inicializamos el hasher recomendado por FastAPI
password_hash = PasswordHash.recommended()

oauth2schema = OAuth2PasswordBearer(tokenUrl="authentication/token")



async def get_user_auth_by_user(user: str, db: Session):
    return db.query(model.Auth).filter(model.Auth.user == user).first()


async def get_users_auth(db: Session):
    users = db.query(model.Auth).all()

    return list(map(schema.Auth.model_validate, users))


async def create_user_auth(schema: schema.AuthCreate, db: Session):
    # Genera el hash seguro (Argon2) automáticamente
    # Soporta cualquier longitud de contraseña sin crashes ni truncados
    secure_hashed_password = password_hash.hash(schema.password)

    user_obj = model.Auth(
        user=schema.user,
        name=schema.name,
        position=schema.position,
        avatar=schema.avatar,
        hashed_password=secure_hashed_password
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj


async def create_token(model: model.Auth):
    user_obj_schema = schema.Auth.model_validate(model)

    token = encode(user_obj_schema.model_dump(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def authenticate_user(user: str, password: str, db: Session):
    user_authenticated = await get_user_auth_by_user(user, db)

    if user_authenticated and user_authenticated.verify_password(password):
        return user_authenticated

    return False


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2schema),
):
    try:
        payload = decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(model.Auth).get(payload["id"])
    except:
        raise HTTPException(
            status_code=401, detail="Usuario y/o Contraseña inválidas"
        )

    return schema.Auth.model_validate(user)


user_authenticated = Depends(get_current_user)