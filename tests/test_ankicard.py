from pathlib import Path

from nanki.modules.ankicard import AnkiCard
from nanki.modules.markdownfile import MarkdownFile

from .helpers import create_and_write


def _create_md_files(
    tmp_path: Path,
    text: str,
    file_name: str = "file.md",
) -> list[MarkdownFile]:

    path = tmp_path / file_name
    create_and_write(path, text)

    return MarkdownFile.load_files(path)


md_before = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
## Front

Front text

## Back

Back text
"""

md_after = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---

<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
"""


def test_writing_back_id(tmp_path: Path) -> None:

    md_files = _create_md_files(tmp_path, md_before)
    anki_cards = AnkiCard.from_markdown_files(md_files)

    # Pretend that a card was uploaded to Anki by setting it's id and created field.
    anki_cards[0].id = 123
    anki_cards[0].created = True

    AnkiCard.write_back_ids(anki_cards)

    assert md_files[0].path.read_text() == md_after


md_before1 = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
## Front

Front text

## Back

Back text
---
## Front

Another front text

## Back

Another back text
"""

md_after1 = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---

<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
---

<!-- nanki_note_id:456 -->

## Front

Another front text

## Back

Another back text
"""


def test_writing_back_multiple_ids(tmp_path: Path) -> None:

    md_files = _create_md_files(tmp_path, md_before1)
    anki_cards = AnkiCard.from_markdown_files(md_files)

    anki_cards[0].id = 123
    anki_cards[0].created = True
    anki_cards[1].id = 456
    anki_cards[1].created = True

    AnkiCard.write_back_ids(anki_cards)

    assert md_files[0].path.read_text() == md_after1


md_before2 = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---

<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
---
## Front

Another front text

## Back

Another back text
"""

md_after2 = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---

<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
---

<!-- nanki_note_id:456 -->

## Front

Another front text

## Back

Another back text
"""


def test_writing_back_single_id_with_one_present(tmp_path: Path) -> None:

    md_files = _create_md_files(tmp_path, md_before2)
    anki_cards = AnkiCard.from_markdown_files(md_files)

    anki_cards[1].id = 456
    anki_cards[1].created = True

    AnkiCard.write_back_ids(anki_cards)

    assert md_files[0].path.read_text() == md_after2


# file that needs to have all 3 cards updated
md1_before = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
## Front

Front text

## Back

Back text
---
## Front

Another front text

## Back

Another back text
---
## Front

Yet another front text

## Back

Yet another back text
"""

md1_after = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---

<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
---

<!-- nanki_note_id:456 -->

## Front

Another front text

## Back

Another back text
---

<!-- nanki_note_id:789 -->

## Front

Yet another front text

## Back

Yet another back text
"""

# file that needs to have none of the cards updated
md2_before = md1_after
md2_after = md1_after

# file that needs to have 1 of the cards updated
md3_before = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---
## Front

Front text

## Back

Back text
---

<!-- nanki_note_id:456 -->

## Front

Another front text

## Back

Another back text
---

<!-- nanki_note_id:789 -->

## Front

Yet another front text

## Back

Yet another back text
"""

md3_after = """---
deck_name: Deck name
note_type_basic: Basic Notetype
note_type_cloze: Cloze Notetype
---

<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
---

<!-- nanki_note_id:456 -->

## Front

Another front text

## Back

Another back text
---

<!-- nanki_note_id:789 -->

## Front

Yet another front text

## Back

Yet another back text
"""


def test_writing_back_complex_example(tmp_path: Path) -> None:
    """Test a complex, realistic scenario.

    Three files are converted into cards and ids are written back

    Three different files are given:

    - file that needs to have all 3 cards updated
    - file that needs to have none of the cards updated
    - file that needs to have 1 of the cards updated
    """
    md1 = _create_md_files(tmp_path, md1_before, "1.md")
    md2 = _create_md_files(tmp_path, md2_before, "2.md")
    md3 = _create_md_files(tmp_path, md3_before, "3.md")

    md_files = md1 + md2 + md3

    anki_cards = AnkiCard.from_markdown_files(md_files)

    # Update all cards in first file
    anki_cards[0].id = 123
    anki_cards[0].created = True
    anki_cards[1].id = 456
    anki_cards[1].created = True
    anki_cards[2].id = 789
    anki_cards[2].created = True

    # Nothing to do for 3-5 (second file) since none of the cards need to be updated.

    # Update only one card in third file
    anki_cards[6].id = 123
    anki_cards[6].created = True

    AnkiCard.write_back_ids(anki_cards)

    assert md_files[0].path.read_text() == md1_after
    assert md_files[1].path.read_text() == md2_after
    assert md_files[2].path.read_text() == md3_after
