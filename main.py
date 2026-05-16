import sys

import config
import classifier
import mover
import toast
import watcher
from menu_bar import SortableApp
from onboarding import run as run_onboarding


def handle_screenshot(path: str) -> None:
    try:
        cfg = config.load()
        folder_name = classifier.classify(path, cfg["folders"], cfg["mode"])

        mover.move(path, cfg["root_folder"], folder_name)
        toast.show(folder_name)

        if cfg["mode"] == "llm" and folder_name != "root":
            if folder_name not in cfg["folders"]:
                cfg["folders"].append(folder_name)
                config.save(cfg)

        config.increment_sorted_count()
    except Exception as e:
        toast.show(f"Error: {e}")


def main():
    cfg = config.load()

    if not cfg.get("root_folder"):
        completed = run_onboarding()
        if not completed:
            sys.exit(0)
        cfg = config.load()

    app = SortableApp()

    obs = watcher.start(
        cfg["root_folder"],
        on_screenshot=handle_screenshot,
    )

    try:
        app.run()
    finally:
        obs.stop()
        obs.join()


if __name__ == "__main__":
    main()
