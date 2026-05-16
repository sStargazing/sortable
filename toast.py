import rumps


def show(folder_name: str) -> None:
    rumps.notification(
        title="Sortable",
        subtitle="",
        message=f"Saved to {folder_name}",
    )


def error(message: str) -> None:
    rumps.notification(
        title="Sortable",
        subtitle="Something went wrong",
        message=message,
    )
