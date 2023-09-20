from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import dbConfig


# ### ---> Modo Testing:
# # Aplicación en modo Local.
# # Base de datos Local SQLite.
# # Conexión local entre aplicación y database.
# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# ### ---> Modo Development:
# # Aplicación en modo Local.
# # Base de datos remota PostgreSQL en GCloudSQL.
# # Conexión remota entre aplicación y database.
# from urllib.parse import quote_plus
# password = quote_plus(dbConfig['password'])
# dbURL = f"postgresql+psycopg2://{dbConfig['username']}:{password}@34.102.109.234/{dbConfig['database']}"
# engine = create_engine(dbURL)


# ---> Modo Production:
# Aplicación en modo remoto en GCloud Run, contenerizada en Docker.
# Base de datos remota PostgreSQL en GCloudSQL.
# Conexión local entre aplicación y database (Unix_Socket entre servidores).
engine = create_engine(URL.create(**dbConfig))


Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
