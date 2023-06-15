from fastapi import FastAPI



app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    # "http://192.168.1.71:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from .router_authentication import router as router_authentication
app.include_router(router_authentication)

from .router_lead import router as router_lead
app.include_router(router_lead)



@app.get("/")
async def home():
    home = {"message": "Conexión exitosa con el servidor"}

    return home



from .orm import Base, engine
Base.metadata.create_all(bind = engine)