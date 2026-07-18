from pathlib import Path

from nanki.modules.ankicard.notesource import NoteSource
from nanki.modules.markdownfile import MarkdownFile

from .helpers import create_and_write


def _create_note_srcs(tmp_path: Path, text: str) -> list[NoteSource]:

    path = tmp_path / "some_file.md"
    create_and_write(path, text)

    md_file = MarkdownFile.load_files(path)[0]
    return NoteSource.from_markdown_file(md_file)


single_note = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
some content
"""


def test_create_a_single_note_source(tmp_path: Path) -> None:

    note_srcs = _create_note_srcs(tmp_path, single_note)

    assert note_srcs[0].path == tmp_path / "some_file.md"
    assert note_srcs[0].start == 5
    assert note_srcs[0].text == "some content"


several_notes = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
some content0
---
some content1
---
some multi
line
content
"""

last_line = """some multi
line
content"""


def test_create_several_notes(tmp_path: Path) -> None:

    note_srcs = _create_note_srcs(tmp_path, several_notes)

    assert len(note_srcs) == 3
    assert note_srcs[0].text == "some content0"
    assert note_srcs[0].start == 5
    assert note_srcs[1].text == "some content1"
    assert note_srcs[1].start == 7
    assert note_srcs[2].text == last_line
    assert note_srcs[2].start == 9


several_notes_with_empty_one = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
some content0
---
---
some content1
"""


def test_create_several_notes_skipping_empty_one(tmp_path: Path) -> None:

    note_srcs = _create_note_srcs(tmp_path, several_notes_with_empty_one)

    assert len(note_srcs) == 2
    assert note_srcs[0].text == "some content0"
    assert note_srcs[0].start == 5
    assert note_srcs[1].text == "some content1"
    assert note_srcs[1].start == 8


several_notes_with_empty_one_in_end = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
some content0
---
some content1
---
"""


def test_create_several_notes_skipping_last_empty_one(tmp_path: Path) -> None:

    note_srcs = _create_note_srcs(tmp_path, several_notes_with_empty_one_in_end)

    assert len(note_srcs) == 2
    assert note_srcs[0].text == "some content0"
    assert note_srcs[0].start == 5
    assert note_srcs[1].text == "some content1"
    assert note_srcs[1].start == 7


no_notes = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
"""


def test_file_with_no_content_should_produce_no_notes(tmp_path: Path) -> None:

    note_srcs = _create_note_srcs(tmp_path, no_notes)

    assert len(note_srcs) == 0
