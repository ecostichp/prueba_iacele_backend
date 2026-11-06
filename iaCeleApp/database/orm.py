import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine.url import URL

from .config import dbConfig


def build_engine():
    # Cloud Run define K_SERVICE. Ahí la base es PostgreSQL por el socket de Cloud SQL.
    # En esta computadora se queda el archivo SQLite.
    if os.getenv("K_SERVICE"):
        return create_engine(
            URL.create(
                drivername="postgresql+psycopg2",
                username=dbConfig["username"],
                password=dbConfig["password"],
                database=dbConfig["database"],
                query={"host": dbConfig["host"]},
            )
        )

    db_file = "local_iaCele.db"
    return create_engine(
        f"sqlite:///./iaCeleApp/database/{db_file}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )


engine = build_engine()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
