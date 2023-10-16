from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://prueba-iacele-frontend.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from .router_authentication import router as router_authentication
app.include_router(router_authentication)

from .router_file_management import router as router_file_management
app.include_router(router_file_management)



from .orm import Base, engine
@app.get("/")
async def home():
    home = {"message": "Conexión exitosa con el servidor"}

    return home



Base.metadata.create_all(bind=engine)
