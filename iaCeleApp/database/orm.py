from pathlib import Path
from typing import Annotated
from urllib.parse import quote_plus
from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine.url import URL

from .config import dbConfig


# ---> Experimental Mode:
# Aplicación en modo Local.
# Base de datos Local SQLite.
# Conexión local entre aplicación y database.
db_path = Path(__file__).resolve().parents[2] / "dbLocalTests" / "dbLocal" / "local_iaCele.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
engine = create_engine( SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30} )


# # ---> Development Mode:
# # Aplicación en modo Local.
# # Base de datos remota PostgreSQL en GCloudSQL.
# # Conexión remota entre aplicación y database.
# password = quote_plus(dbConfig['password'])
# dbURL = f"postgresql+psycopg2://{dbConfig['username']}:{password}@{dbConfig['sql_ip_public']}/{dbConfig['database']}"
# engine = create_engine(dbURL)


# # ---> Production Mode:
# # Aplicación en modo remoto en GCloud Run, contenerizada en Docker.
# # Base de datos remota PostgreSQL en GCloudSQL.
# # Conexión local entre aplicación y database (Unix_Socket entre servidores).
# engine = create_engine(URL.create(**dbConfig))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

