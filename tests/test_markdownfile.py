from pathlib import Path

import pytest

from nanki.modules.markdownfile import MarkdownFile

from .helpers import create_and_write

good_md = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
some content
"""


def test_create_a_single_md_file(tmp_path: Path) -> None:
    p = tmp_path / "good.md"
    create_and_write(p, good_md)

    md_file = MarkdownFile.load_files(p)[0]

    assert md_file.content == good_md
    assert md_file.path == p
    assert md_file.metadata.deck_name == "Deck name"


def test_create_non_existing_md_file(tmp_path: Path) -> None:
    p = tmp_path / "doesnt_exist.md"

    with pytest.raises(
        ValueError,
        match="Invalid path was given, it isn't a file nor a directory",
    ):
        MarkdownFile.load_files(p)


def test_create_several_files(tmp_path: Path) -> None:
    files = [
        "good1.md",
        "good2.md",
        "dir_a/good3.md",
        "dir_a/good4.md",
        "dir_a/dir_b/good5.md",
    ]
    empty_files = [
        "empty1.md",
        "empty2.md",
        "dir_a/empty3.md",
        "dir_a/empty4.md",
        "dir_a/dir_b/empty5.md",
    ]

    # Create good markdown files
    paths = [tmp_path / p for p in files]

    for p in paths:
        create_and_write(p, good_md)

    # Create empty markdown files
    empty_paths = [tmp_path / p for p in empty_files]

    for p in empty_paths:
        create_and_write(p)

    # Load from the top dir
    md_files = MarkdownFile.load_files(tmp_path)

    # Names of all good markdown files should be present
    names = [f.path.name for f in md_files]

    for p in paths:
        assert p.name in names

    assert len(names) == len(files)

    # None of the empty ones should be present
    for p in empty_files:
        assert p not in names
