from fastapi import FastAPI


# Se instancía la clase para generar el objeto 'app'. Este es el módulo principal.
app = FastAPI()



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



# Se importan las librería necesaria para el manejo de la descarga de archivos estáticos
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="iaCeleApp/static"), name="static")



# Ruta principal
@app.get("/")
async def home():
    home = {"message": "Conexión exitosa con el servidor"}

    return home



# Se integran las rutas de las subapps.
from .authentication import router as authentication
app.include_router(authentication.router)

from .usuarios import router as usuarios
app.include_router(usuarios.router)

from .productos import router as productos
app.include_router(productos.router)

from .file_management import router as file_management
app.include_router(file_management.router)



# Se agrega el ORM ya que integramos las subapps para que se creen todas las tablas en la base de datos.
from .database import Base, engine
Base.metadata.create_all(bind=engine)
