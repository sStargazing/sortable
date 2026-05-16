import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULTS = {
    "root_folder": "",
    "mode": "existing",  # or "llm"
    "folders": [],
    "sorted_count": 0,
}


def load() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return dict(DEFAULTS)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save(cfg: dict) -> None:
    if "folders" in cfg:
        cfg["folders"]=clean_folders(cfg["folders"])

    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def increment_sorted_count() -> int:
    cfg = load()
    cfg["sorted_count"] += 1
    save(cfg)
    return cfg["sorted_count"]

def clean_folders(folders: list[str]) -> list[str]:
    cleaned=[]
    for folder in folders:
        folder=folder.strip()
        if folder and folder not in cleaned:
            cleaned.append(folder)
    return cleaned