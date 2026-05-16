import rumps

import config


class SortableApp(rumps.App):
    def __init__(self):
        cfg = config.load()
        count = cfg.get("sorted_count", 0)
        super().__init__("Sortable", title=self._label(count))

    @staticmethod
    def _label(count: int) -> str:
        return f"Sorted {count} screenshot{'s' if count != 1 else ''}"

    @rumps.timer(2)
    def sync_count(self, _):
        cfg = config.load()
        self.title = self._label(cfg.get("sorted_count", 0))

    @rumps.clicked("Quit")
    def quit(self, _):
        rumps.quit_application()
