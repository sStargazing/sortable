import rumps
from AppKit import NSAlert, NSOpenPanel

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


def _alert(title: str, message: str, *buttons: str) -> int:
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    for btn in buttons:
        alert.addButtonWithTitle_(btn)
    return alert.runModal()


class SortableApp(rumps.App):
    def __init__(self, on_folder_change=None, on_ready=None):
        cfg = config.load()
        count = cfg.get("sorted_count", 0)
        self._on_folder_change = on_folder_change
        self._on_ready = on_ready

        self._mode_item = rumps.MenuItem(
            self._mode_label(cfg.get("mode", "llm")),
            callback=self._switch_mode,
        )

        super().__init__(
            "Sortable",
            title=self._label(count),
            menu=[
                self._mode_item,
                rumps.MenuItem("Change Screenshot Folder…", callback=self._change_folder),
            ],
        )

    @staticmethod
    def _label(count: int) -> str:
        return f"Sorted {count} screenshot{'s' if count != 1 else ''}"

    @staticmethod
    def _mode_label(mode: str) -> str:
        return "Switch to: Use Existing Folders" if mode == "llm" else "Switch to: LLM Creates Folders"

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
        self._mode_item.title = self._mode_label(cfg.get("mode", "llm"))

    def _change_folder(self, _):
        folder = _pick_folder("Select Folder")
        if not folder:
            return
        cfg = config.load()
        cfg["root_folder"] = folder
        config.save(cfg)
        if self._on_folder_change:
            self._on_folder_change(folder)

    def _switch_mode(self, _):
        cfg = config.load()
        new_mode = "existing" if cfg["mode"] == "llm" else "llm"

        cfg["folders"] = []

        cfg["mode"] = new_mode
        config.save(cfg)
        self._mode_item.title = self._mode_label(new_mode)
