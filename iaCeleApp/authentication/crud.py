from sqlmodel  import Session, select
from datetime import datetime, timezone
from typing import Annotated
from fastapi import HTTPException, Depends
from jwt import encode, decode
from pwdlib import PasswordHash 
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

from . import schema
from ..database import SessionDep


JWT_SECRET = "acdebbc350cbe8730b24198ae98015f38ea64e72857d0b14c51370b5a60d3e57"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

# Inicializamos el hasher recomendado por FastAPI
password_hash = PasswordHash.recommended()

# Aquí le dices al DOCS de fastapi dónde buscar el token para usar los endpoint que ocupan autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authentication/token")


def password_hashed_func(password_str: str) -> str:
    return password_hash.hash(password_str)


async def read_by_username(username: str, session: Session):

    statement = select(schema.Authentications).where(schema.Authentications.username == username)

    return session.exec(statement).first()


async def read_by_employee_id(key: id, session: Session):

    statement = select(schema.Authentications).where(schema.Authentications.empleado_id == key)

    return session.exec(statement).first()


async def read_by_id(id: int, session: Session):

    return session.get(schema.Authentications, id)


async def create(new_obj: schema.AuthenticationsCreate, session: Session):
    
    default_password = '123456'
    obj_data = new_obj.model_dump()
    obj_data['password_hashed'] = password_hashed_func(default_password)

    db_obj = schema.Authentications(**obj_data)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def update(existing_obj:schema.Authentications, obj_new_vals: schema.AuthenticationsUpdate, session: Session):
    
    obj_new_data = obj_new_vals.model_dump(
        exclude = {
            'password_str'
        }
    )
    obj_new_data['password_hash'] = password_hashed_func(obj_new_vals.password_str)

    db_obj = existing_obj.sqlmodel_update(obj_new_data)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def delete(existing_obj:schema.Authentications, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Usuario de aplicación borrado con éxito'



async def change_in_authentication(obj, session: Session):

    user = await read_by_employee_id(obj['id'], session)
    
    if not user and obj['is_app_user'] == True:
        return await create(obj, session)
    elif user and obj['is_app_user'] == False:
        return await delete(user, session)

    return 'Usuario de aplicación borrado con éxito'













async def authenticate_user(username: str, password_str: str, session: Session)-> schema.Authentications|None:
    user_authenticated = await read_by_username(username, session)

    if user_authenticated and user_authenticated.verify_password(password_str):
        return user_authenticated

    return None


async def create_token(user_authenticated: schema.Authentications)-> schema.Token:
    
    user_authenticated_data = user_authenticated.model_dump(
        exclude = {
            'avatar',
            'fecha_alta'
        }
    )
    user_authenticated_data['exp'] = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    token = encode(user_authenticated_data, JWT_SECRET, algorithm=ALGORITHM)

    return schema.Token(access_token=token, token_type="bearer")


async def get_current_user_from_token(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):

    try:
        # El decode puede fallar si el token no lleva los segmentos necesarios.
        payload = decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        # Si la función no encuentra el id, retornará None. 
        # Además, si por alguna razón el payload no tiene la llave 'id' y rompe la función, se va al exception.
        return await read_by_id(payload['id'], session)
    
    except:
        return None


async def require_user_authenticated(current_user: Annotated[schema.Authentications, Depends(get_current_user_from_token)]):
    if not current_user:
        raise HTTPException(
            status_code=401, 
            detail="Credenciales inválidas o token expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user

authentication_require = Depends(require_user_authenticated)
