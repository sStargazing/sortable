import os
import shutil


def move(image_path: str, root_folder: str, folder_name: str) -> str:
    """Move image_path into root_folder/folder_name, creating the dir if needed.

    Returns the destination path.
    """
    if folder_name == "root":
        dest_dir = root_folder
    else:
        dest_dir = os.path.join(root_folder, folder_name)

    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(image_path))
    shutil.move(image_path, dest)
    return dest
