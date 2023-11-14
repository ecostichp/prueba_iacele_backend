from fastapi import APIRouter, UploadFile
from fastapi.responses import HTMLResponse


from . import crud
from ..authentication import user_authenticated


router = APIRouter(
    tags=["file_management"],
    prefix='/file_management',
    responses={404: {"description": "Not found"}},
)



@router.get("/", dependencies=[user_authenticated])
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


@router.post("/uploadfiles/", dependencies=[user_authenticated])
async def upload_files(files: list[UploadFile]):

    if files[0].filename == "":
        return {'message': 'No upload files sent'}
    else:
        return await crud.save_files(files)



@router.get("/{file_name}/")
async def get_file(file_name: str):

    return await crud.get_file(file_name)



@router.get("/download/{file_name}/", dependencies=[user_authenticated])
async def download_file(file_name: str):

    return await crud.download_file(file_name)



@router.delete("/{file_name}/", dependencies=[user_authenticated])
async def delete_file(file_name: str):

    return await crud.delete_file(file_name)