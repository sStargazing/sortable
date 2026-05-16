import tkinter as tk
from tkinter import filedialog, messagebox

import config


def run() -> bool:
    """Show the two-screen onboarding wizard. Returns True if completed."""
    root = tk.Tk()
    root.withdraw()

    # Screen 1 — pick root screenshot folder
    root_folder = filedialog.askdirectory(title="Select your screenshot folder")
    if not root_folder:
        return False

    # Screen 2 — pick mode
    mode_win = tk.Toplevel()
    mode_win.title("Sortable")
    mode_win.resizable(False, False)
    mode = tk.StringVar(value="")

    tk.Label(mode_win, text="How should folders be managed?", pady=12, padx=16).pack()

    def pick(value):
        mode.set(value)
        mode_win.destroy()

    tk.Button(mode_win, text="Use existing folders", width=24,
              command=lambda: pick("existing")).pack(pady=4)
    tk.Button(mode_win, text="LLM creates folders", width=24,
              command=lambda: pick("llm")).pack(pady=4)

    mode_win.grab_set()
    root.wait_window(mode_win)

    if not mode.get():
        return False

    folders = []
    if mode.get() == "existing":
        messagebox.showinfo("Sortable", "Now select the folders you want to sort into.")
        while True:
            folder = filedialog.askdirectory(title="Add a folder (cancel when done)")
            if not folder:
                break
            name = folder.split("/")[-1]
            folders.append(name)
        if not folders:
            messagebox.showwarning("Sortable", "No folders selected. Exiting.")
            return False

    cfg = config.load()
    cfg["root_folder"] = root_folder
    cfg["mode"] = mode.get()
    cfg["folders"] = folders
    config.save(cfg)

    root.destroy()
    return True
