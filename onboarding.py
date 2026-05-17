import os

from AppKit import NSAlert, NSOpenPanel, NSApp, NSApplication
import objc

NSModalResponseOK = 1


def _ensure_app():
    NSApplication.sharedApplication()
    NSApp.activateIgnoringOtherApps_(True)


def _pick_folder(title: str, prompt: str) -> str | None:
    panel = NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(False)
    panel.setCanChooseDirectories_(True)
    panel.setAllowsMultipleSelection_(False)
    panel.setTitle_(title)
    panel.setPrompt_(prompt)
    if panel.runModal() == NSModalResponseOK:
        return str(panel.URLs()[0].path())
    return None


def _alert(title: str, message: str, *buttons: str) -> int:
    """Show a native alert. Returns 1000 for first button, 1001 for second, etc."""
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    for btn in buttons:
        alert.addButtonWithTitle_(btn)
    return alert.runModal()


import config


def run() -> bool:
    _ensure_app()

    # Screen 1 — explain then pick screenshot folder
    _alert(
        "Welcome to Sortable",
        "First, select the folder where your Mac saves screenshots.\n\n"
        "This is usually your Desktop. You can check by pressing ⌘⇧5 "
        "and looking at the \"Save to\" option.",
        "Choose Folder…",
    )
    root_folder = _pick_folder("Select Screenshot Folder", "Select")
    if not root_folder:
        return False

    # Check folder access
    try:
        os.listdir(root_folder)
    except PermissionError:
        _alert(
            "Permission needed",
            f"Sortable needs access to:\n{root_folder}\n\n"
            "Go to System Settings → Privacy & Security → Files and Folders "
            "and enable access for Terminal.",
            "OK",
        )
        return False

    # Screen 2 — pick mode
    response = _alert(
        "How should folders be managed?",
        "Use existing folders: Sortable sorts into folders already in your screenshot folder.\n\n"
        "LLM creates folders: Sortable names and creates folders automatically.",
        "Use existing folders",
        "LLM creates folders",
    )
    # 1000 = first button, 1001 = second button
    mode = "existing" if response == 1000 else "llm"

    cfg = config.load()
    cfg["root_folder"] = root_folder
    cfg["mode"] = mode
    cfg["folders"] = []
    config.save(cfg)
    return True
