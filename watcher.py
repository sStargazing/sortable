import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

STABLE_POLL_INTERVAL = 0.2  # seconds
STABLE_TIMEOUT = 5  # seconds


def _wait_for_stable(path: str) -> bool:
    """Poll until file size stops changing. Returns False on timeout."""
    prev_size = -1
    deadline = time.time() + STABLE_TIMEOUT
    while time.time() < deadline:
        try:
            size = os.path.getsize(path)
        except FileNotFoundError:
            return False
        if size == prev_size:
            return True
        prev_size = size
        time.sleep(STABLE_POLL_INTERVAL)
    return False


class ScreenshotHandler(FileSystemEventHandler):
    EXTENSIONS = {".png", ".jpg"}

    def __init__(self, on_screenshot):
        self._on_screenshot = on_screenshot
        self._seen = set()

    def _handle(self, path: str) -> None:
        name = os.path.basename(path)
        if name in self._seen:
            return
        if name.startswith("."):
            return
        self._seen.add(name)
        print(f"[watcher] detected: {path}", flush=True)
        if os.path.splitext(path)[1].lower() not in self.EXTENSIONS:
            return
        if _wait_for_stable(path):
            self._on_screenshot(path)

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle(event.dest_path)


def start(folder: str, on_screenshot) -> Observer:
    handler = ScreenshotHandler(on_screenshot)
    observer = Observer()
    observer.schedule(handler, folder, recursive=False)
    observer.start()
    print(f"[watcher] watching: {folder}")
    return observer
