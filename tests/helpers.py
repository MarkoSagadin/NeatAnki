from pathlib import Path


def create_and_write(path: str | Path, content: str = "") -> None:
    """Create a file on the given path with the given content.

    Args:
        path (str):         Path from where to create the filename.
        content (str):      File content to write. If None, nothing is written.

    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
