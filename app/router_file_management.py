from fastapi import APIRouter, UploadFile, Depends
from fastapi.responses import HTMLResponse


from . import crud_file_management, schema, crud_authentication


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
async def create_upload_files(files: list[UploadFile], current_user: schema.User = Depends(crud_authentication.get_current_user)):

     return await crud_file_management.save_files(files)
