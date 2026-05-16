import subprocess


def show(folder_name: str) -> None:
    """Display a macOS notification."""
    title = "Sortable"
    message = f"Saved to {folder_name}"
    script = (
        f'display notification "{message}" with title "{title}"'
    )
    subprocess.run(["osascript", "-e", script], check=False)
