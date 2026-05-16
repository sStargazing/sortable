import os

import config
import watcher
import toast
import mover
import classifier
from menu_bar import SortableApp


def get_folder_names(cfg):
    if cfg["mode"]=="existing":
        folders=[]

        for item in os.listdir(cfg["root_folder"]):
            path=os.path.join(cfg["root_folder"],item)

            if os.path.isdir(path) and not item.startswith("."):
                folders.append(item)

        return folders

    names=[]

    for folder in cfg["folders"]:
        if isinstance(folder, dict):
            names.append(folder["name"])
        else:
            names.append(folder)

    return names


def handle_screenshot(path: str) -> None:
    try:
        print(f"[handle] classifying {path}", flush=True)

        cfg=config.load()
        folder_names=get_folder_names(cfg)

        print(f"[handle] available folders: {folder_names}", flush=True)

        folder_name=classifier.classify(path, folder_names, cfg["mode"])
        print(f"[handle] classified as: {folder_name}", flush=True)

        if cfg["mode"]=="existing":
            if folder_name not in folder_names and folder_name!="root":
                print("[handle] invalid folder from AI, using root", flush=True)
                folder_name="root"

        mover.move(path, cfg["root_folder"], folder_name)
        print("[handle] moved", flush=True)

        toast.show(folder_name)

        if cfg["mode"]=="llm" and folder_name!="root":
            if folder_name not in folder_names:
                cfg["folders"].append(folder_name)
                config.save(cfg)

        config.increment_sorted_count()

    except Exception as e:
        print(f"[handle] ERROR: {e}", flush=True)
        toast.error(str(e))


def main():
    print("[sortable] starting...", flush=True)
    obs_ref=[None]

    def start_watcher():
        cfg=config.load()
        obs_ref[0]=watcher.start(
            cfg["root_folder"],
            on_screenshot=handle_screenshot
        )

    def on_folder_change(new_folder):
        if obs_ref[0]:
            obs_ref[0].stop()
            obs_ref[0].join()

        obs_ref[0]=watcher.start(
            new_folder,
            on_screenshot=handle_screenshot
        )

    app=SortableApp(
        on_folder_change=on_folder_change,
        on_ready=start_watcher
    )

    try:
        app.run()
    finally:
        if obs_ref[0]:
            obs_ref[0].stop()
            obs_ref[0].join()


if __name__=="__main__":
    main()