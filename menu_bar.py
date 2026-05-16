import rumps
from AppKit import NSOpenPanel

import config


def _pick_folder(prompt: str) -> str | None:
    panel = NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(False)
    panel.setCanChooseDirectories_(True)
    panel.setAllowsMultipleSelection_(False)
    panel.setPrompt_(prompt)
    panel.setTitle_("Sortable")
    if panel.runModal() == 1:
        return str(panel.URLs()[0].path())
    return None


class SortableApp(rumps.App):
    def __init__(self, on_folder_change=None, on_ready=None):
        cfg = config.load()
        count = cfg.get("sorted_count", 0)
        super().__init__("Sortable", title=self._label(count))
        self._on_folder_change = on_folder_change
        self._on_ready = on_ready

    @staticmethod
    def _label(count: int) -> str:
        return f"Sorted {count} screenshot{'s' if count != 1 else ''}"

    @rumps.timer(0.5)
    def _startup(self, timer):
        timer.stop()
        print("[sortable] app running, checking config...", flush=True)
        cfg = config.load()
        if not cfg.get("root_folder"):
            from onboarding import run as run_onboarding
            if not run_onboarding():
                rumps.quit_application()
                return
        print(f"[sortable] watching: {config.load()['root_folder']}", flush=True)
        if self._on_ready:
            self._on_ready()

    @rumps.timer(2)
    def sync_count(self, _):
        cfg = config.load()
        self.title = self._label(cfg.get("sorted_count", 0))

    @rumps.clicked("Change Screenshot Folder…")
    def change_folder(self, _):
        folder = _pick_folder("Select Folder")
        if not folder:
            return
        cfg = config.load()
        cfg["root_folder"] = folder
        config.save(cfg)
        if self._on_folder_change:
            self._on_folder_change(folder)
