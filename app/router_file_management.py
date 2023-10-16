from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi import UploadFile


from . import crud_file_management


router = APIRouter(
    tags=["file_management"],
    prefix='/file_management',
    responses={404: {"description": "Not found"}},
)



@router.get("/")
async def main():
    content = """
<body>
<form action="/file_management/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)



@router.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):

     return await crud_file_management.save_files(files)
