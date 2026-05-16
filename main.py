import config
import watcher
import toast
import mover
import classifier
from menu_bar import SortableApp
from onboarding import run as run_onboarding
import rumps


def handle_screenshot(path: str) -> None:
    try:
        print(f"[handle] classifying {path}", flush=True)
        cfg = config.load()
        folder_name = classifier.classify(path, cfg["folders"], cfg["mode"])
        print(f"[handle] classified as: {folder_name}", flush=True)

        mover.move(path, cfg["root_folder"], folder_name)
        print(f"[handle] moved", flush=True)
        toast.show(folder_name)

        if cfg["mode"] == "llm" and folder_name != "root":
            if folder_name not in cfg["folders"]:
                cfg["folders"].append(folder_name)
                config.save(cfg)

        config.increment_sorted_count()
    except Exception as e:
        print(f"[handle] ERROR: {e}", flush=True)
        toast.error(str(e))


def main():
    print("[sortable] starting...", flush=True)
    obs_ref = [None]

    def start_watcher():
        cfg = config.load()
        obs_ref[0] = watcher.start(cfg["root_folder"], on_screenshot=handle_screenshot)

    def on_folder_change(new_folder):
        if obs_ref[0]:
            obs_ref[0].stop()
            obs_ref[0].join()
        obs_ref[0] = watcher.start(new_folder, on_screenshot=handle_screenshot)

    app = SortableApp(on_folder_change=on_folder_change, on_ready=start_watcher)

    try:
        app.run()
    finally:
        if obs_ref[0]:
            obs_ref[0].stop()
            obs_ref[0].join()


if __name__ == "__main__":
    main()
