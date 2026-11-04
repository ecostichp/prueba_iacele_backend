from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse


from . import crud
from ..authentication import authentication_require


router = APIRouter(
    tags=["file_management"],
    prefix='/file_management',
    responses={404: {"description": "Not found"}},
    dependencies=[authentication_require],
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
async def upload_files(file: UploadFile = File(...)):

    if file.filename == "":
        return {'message': 'No upload file sent'}
    else:
        return await crud.save_files(file)



@router.get("/{file_name}/")
async def get_file(file_name: str):

    return await crud.get_file(file_name)



@router.get("/download/{file_name}/")
async def download_file(file_name: str):

    return await crud.download_file(file_name)



@router.delete("/{file_name}/")
async def delete_file(file_name: str):

    return await crud.delete_file(file_name)