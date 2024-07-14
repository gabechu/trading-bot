from pathlib import Path


def create_directory(filepath: str) -> None:
    path = Path(filepath)

    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)
