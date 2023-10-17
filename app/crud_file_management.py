from pathlib import Path
import shutil


upload_dir_name = "uploadfiles"
upload_dir_path = Path.joinpath(Path.cwd(), upload_dir_name)



async def save_files(files):
    
    upload_dir_path.mkdir(parents=True, exist_ok=True)

    for file in files:

     # get the destination path
        dest = Path.joinpath(upload_dir_path, file.filename)

        # copy the file contents
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print("\nSe subió el archivo:", file.filename)
        print("En el Path", dest)

    return {"filenames": [file.filename for file in files]}
