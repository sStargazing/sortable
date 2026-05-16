import os
import shutil


def unique_path(path: str) -> str:
    if not os.path.exists(path):
        return path

    folder=os.path.dirname(path)
    filename=os.path.basename(path)
    name,ext=os.path.splitext(filename)

    counter=2
    while True:
        new_path=os.path.join(folder, f"{name} ({counter}){ext}")
        if not os.path.exists(new_path):
            return new_path
        counter+=1


def move(image_path: str, root_folder: str, folder_name: str) -> str:
    if folder_name=="root":
        dest_dir=root_folder
    else:
        dest_dir=os.path.join(root_folder, folder_name)

    os.makedirs(dest_dir, exist_ok=True)

    dest=os.path.join(dest_dir, os.path.basename(image_path))
    dest=unique_path(dest)

    shutil.move(image_path, dest)
    return dest