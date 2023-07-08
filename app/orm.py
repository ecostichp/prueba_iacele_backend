from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings



DATABASE_URL = f"postgresql+psycopg2://{settings.gcloud_sql_user}:{settings.gcloud_sql_password}@{settings.gcloud_sql_host}/{settings.gcloud_sql_db}"
engine = create_engine( DATABASE_URL )


# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False} )



Base = declarative_base()



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()