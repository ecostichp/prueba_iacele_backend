from fastapi.responses import FileResponse
from pathlib import Path
import shutil


upload_dir_name = "uploadfiles"
upload_dir_path = Path.joinpath(Path.cwd(), upload_dir_name)
upload_dir_path.mkdir(parents=True, exist_ok=True)



async def save_files(files):
    
    for file in files:
        
        # get the destination path
        file_path = Path.joinpath(upload_dir_path, file.filename)

        # copy the file contents
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
    return {"filenames": [file.filename for file in files]}



async def check_file_exist(file_name):

    file_path = Path.joinpath(upload_dir_path, file_name)
    
    return file_path.exists(), file_path



async def get_file(file_name):
    
    file_exist, file_path = await check_file_exist(file_name)

    if file_exist:
        return FileResponse(file_path)
    else:
        return {'message': "File doesn't exist"}
    


async def download_file(file_name):
    
    file_exist, file_path = await check_file_exist(file_name)

    if file_exist:
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    else:
        return {'message': "File doesn't exist"}



async def delete_file(file_name):
    
    file_exist, file_path = await check_file_exist(file_name)

    if file_exist:
        return file_path.unlink()
    else:
        return {'message': 'File does not exist'}