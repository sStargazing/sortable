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

    def on_created(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext not in self.EXTENSIONS:
            return
        if _wait_for_stable(event.src_path):
            self._on_screenshot(event.src_path)


def start(folder: str, on_screenshot) -> Observer:
    """Start watching folder; calls on_screenshot(path) for each new image."""
    handler = ScreenshotHandler(on_screenshot)
    observer = Observer()
    observer.schedule(handler, folder, recursive=False)
    observer.start()
    return observer
