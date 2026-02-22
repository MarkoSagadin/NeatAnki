from dataclasses import dataclass
from pathlib import Path
from typing import Self


@dataclass
class FileData:
    path: Path
    content: str

    @classmethod
    def from_path(cls, path: Path) -> Self:
        """Create FileData from path."""
        return cls(path=path, content=path.read_text(encoding="utf-8"))

    def write(self, path: Path | None = None) -> None:
        """Write to the File.

        If path is given then prepend it to internal path before writing.
        """
        path_to_write = self.path

        if path:
            path_to_write = path / path_to_write

        path_to_write.parent.mkdir(parents=True, exist_ok=True)
        path_to_write.write_text(self.content, encoding="utf-8")
