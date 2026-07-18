import re
from dataclasses import dataclass
from pathlib import Path

from nanki.modules.markdownfile import MarkdownFile


@dataclass
class NoteSource:
    # Path to the source markdown file.
    path: Path
    # Line index in the source file containing the start of note, immediately after
    # frontmatter or "---" marker.
    start: int
    # Note text
    text: str

    @classmethod
    def from_markdown_file(cls, md: MarkdownFile) -> list["NoteSource"]:
        """Create a list of NoteSource instances from a single MarkdownFile."""
        marker_pattern = r"(?m)^(?:---+?)$"  # Match hr in markdown

        note_srcs = []

        prev_note_start = 0
        lines = md.content.splitlines()

        def capture_non_empty(text: str) -> None:
            if text.strip():
                note_srcs.append(cls(md.path, prev_note_start, text))

        # Iterate through all lines and look for markers. When marker is found, extract
        # the text between the previous marker and current one.
        for idx, line in enumerate(lines):
            if re.match(marker_pattern, line):
                text = "\n".join(lines[prev_note_start:idx])

                # Skip empty sections
                capture_non_empty(text)

                # Plus one is added to skip the current line with the marker.
                prev_note_start = idx + 1

        # Capture also the end if it isn't empty
        text = "\n".join(lines[prev_note_start:])
        capture_non_empty(text)

        # Remove first note source, as that is always the frontmatter block.
        return note_srcs[1:]
