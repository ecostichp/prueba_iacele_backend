from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router_authentication import router as router_authentication
from .orm import Base, engine


app = FastAPI()


origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router_authentication)


@app.get("/")
async def home():
    home = {"message": "Conexión exitosa con el servidor"}

    return home


Base.metadata.create_all(bind=engine)
