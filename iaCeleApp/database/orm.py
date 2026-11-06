from pathlib import Path
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine.url import URL

from .config import settings


def cloudsql_socket_dir() -> str:
    socket_dir = settings.gcloud_sql_name.strip()
    if not socket_dir.startswith("/"):
        socket_dir = f"/cloudsql/{socket_dir}"
    return socket_dir


def build_engine():
    mode = settings.db_mode.strip().lower()

    if mode == "sqlite":
        db_path = Path(__file__).resolve().parents[2] / "dbLocalTests" / "dbLocal" / "local_iaCele.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"DB_MODE=sqlite ({db_path})")
        return create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False, "timeout": 30},
        )

    if mode == "postgres":
        print(f"DB_MODE=postgres ({settings.gcloud_sql_ip}/{settings.gcloud_sql_db})")
        return create_engine(
            URL.create(
                drivername="postgresql+psycopg2",
                username=settings.gcloud_sql_user,
                password=settings.gcloud_sql_password,
                host=settings.gcloud_sql_ip,
                port=5432,
                database=settings.gcloud_sql_db,
                query={"gssencmode": "disable"},
            ),
            pool_pre_ping=True,
        )

    if mode == "cloudsql":
        socket_dir = cloudsql_socket_dir()
        print(f"DB_MODE=cloudsql ({socket_dir}/{settings.gcloud_sql_db})")
        return create_engine(
            URL.create(
                drivername="postgresql+psycopg2",
                username=settings.gcloud_sql_user,
                password=settings.gcloud_sql_password,
                database=settings.gcloud_sql_db,
                query={
                    "host": socket_dir,
                    # El proxy de Cloud Run cierra el socket si libpq intenta GSS o SSL.
                    "gssencmode": "disable",
                    "sslmode": "disable",
                },
            ),
            pool_pre_ping=True,
        )

    raise RuntimeError(
        f"DB_MODE '{settings.db_mode}' no es válido. Usa sqlite, postgres o cloudsql."
    )


engine = build_engine()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

