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


from pathlib import Path
from fastapi import UploadFile
import shutil


@app.post("/uploadfiles/")
async def create_upload_file(file: UploadFile):
    upload_dir = Path.joinpath(Path.cwd(), "uploadfiles")

    upload_dir.mkdir(parents=True, exist_ok=True)

    # get the destination path
    dest = Path.joinpath(upload_dir, file.filename)
    
    print(dest)

    # copy the file contents
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}




Base.metadata.create_all(bind=engine)
