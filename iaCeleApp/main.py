from fastapi import FastAPI

# Se agrega el ORM ya que integramos las subapps para que se creen todas las tablas en la base de datos.
from contextlib import asynccontextmanager
from .database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar el servidor (Reemplaza a @app.on_event("startup"))
    create_db_and_tables()
    from sqlmodel import Session

    from .database.orm import engine
    from .inventario.crud import repair_help_assignments

    with Session(engine) as session:
        repair_help_assignments(session)
    
    yield # Aquí la API se queda escuchando peticiones
    
    # Aquí puedes poner código si necesitaras limpiar algo al apagar (Shutdown)

# 2. Inicializar FastAPI pasándole el lifespan
app = FastAPI(lifespan=lifespan)



# Se importa los CORS para que el frontend pueda hacer peticiones al backend
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://prueba-iacele-frontend.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ruta principal
@app.get("/")
async def home():
    home = {"message": "Conexión exitosa con el servidor"}

    return home



# Se integran las rutas de las subapps.
from .authentication import router as authentication
app.include_router(authentication.router)

from .empleados import router as empleados
app.include_router(empleados.router)

from .equipos import router as equipos
app.include_router(equipos.router)

from .productos import router as productos
app.include_router(productos.router)

from .inventario import router as inventario
app.include_router(inventario.router)

from .file_management import router as file_management
app.include_router(file_management.router)
