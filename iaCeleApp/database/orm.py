from pathlib import Path
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine.url import URL

from .config import settings


def cloudsql_instance_name() -> str:
    name = settings.gcloud_sql_name.strip().strip('"').strip("'")
    if name.startswith("/cloudsql/"):
        name = name[len("/cloudsql/"):]
    suffix = "/.s.PGSQL.5432"
    if name.endswith(suffix):
        name = name[: -len(suffix)]
    return name


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
                query={
                    "gssencmode": "disable",
                    "sslnegotiation": "postgres",
                },
            ),
            pool_pre_ping=True,
        )

    if mode == "cloudsql":
        from google.cloud.sql.connector import Connector

        instance = cloudsql_instance_name()
        connector = Connector(ip_type="public", refresh_strategy="background")

        def getconn():
            return connector.connect(
                instance,
                "psycopg",
                user=settings.gcloud_sql_user,
                password=settings.gcloud_sql_password,
                db=settings.gcloud_sql_db,
            )

        print(f"DB_MODE=cloudsql ({instance}/{settings.gcloud_sql_db})")
        return create_engine(
            "postgresql+psycopg://",
            creator=getconn,
            pool_pre_ping=True,
            pool_size=8,
            max_overflow=8,
            pool_timeout=20,
            pool_recycle=1800,
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

