import logging
import re
from dataclasses import dataclass
from enum import Enum
from itertools import groupby
from typing import Any

from nanki.modules.ankicard.notesource import NoteSource
from nanki.modules.ankicard.process_card.compile import card_fields_to_html_text
from nanki.modules.ankicard.process_clozes import HandleClozes, are_clozes_in_card
from nanki.modules.ankicard.utils.card_error import CardError
from nanki.modules.markdownfile import MarkdownFile, MarkdownMetadata

log = logging.getLogger(__name__)


class CardType(Enum):
    Basic = 0
    Cloze = 1


@dataclass
class AnkiCard:
    """Data class representing an Anki card."""

    metadata: MarkdownMetadata
    fields: dict
    card_type: CardType
    note_src: NoteSource
    id: int | None

    # Can be set later by AnkiConnect code to mark, if the card had to be newly created
    # and id was set at that time. Use to filter out AnkiCards that need to have id
    # marker written back int their source markdown file from which they were generated
    # from.
    created: bool = False

    @classmethod
    def from_markdown_files(cls, mds: list[MarkdownFile]) -> list["AnkiCard"]:
        """Create Anki Cards from Markdown files."""

        def flatten(xss: list[Any]) -> list[Any]:
            return [x for xs in xss for x in xs]

        return flatten([cls.from_markdown_file(md) for md in mds])

    @classmethod
    def from_markdown_file(cls, md: MarkdownFile) -> list["AnkiCard"]:
        """Create Anki Cards from a single Markdown file."""
        note_srcs = NoteSource.from_markdown_file(md)

        cards = []
        try:
            for note_src in note_srcs:
                if are_clozes_in_card(note_src.text):
                    clozes_handler = HandleClozes(note_src.text)
                    fields, card_id = _extract_fields_and_id_from_card_text(
                        clozes_handler.hashed_markdown,
                    )
                    fields = clozes_handler.inject_clozes(fields)
                    card_type = CardType.Cloze
                else:
                    fields, card_id = _extract_fields_and_id_from_card_text(
                        note_src.text,
                    )
                    card_type = CardType.Basic

                card = cls(md.metadata, fields, card_type, note_src, card_id)
                cards.append(card)

        except CardError as error:
            # TODO: adjust the final error message
            log.info(
                f"\n📔 This is the card that created the error:📔\n{note_src.text}\n\n"
                "(see card above)",
            )
            log.error(error)
            raise

        return cards

    @staticmethod
    def write_back_ids(anki_cards: list["AnkiCard"]) -> None:
        """Write back the ids of newly created cards into their source md files.

        This is done in particular way:
        1. Extract only cards that were just created in Anki
        2. Sort them and group them by common source files
        3. Start adding marker line to the newly created card from bottom to up.

        Why from bottom to up? If the other way would be done then as soon as the first
        marker would be inserted, other card.note_src.start would be wrong.
        """
        # Extract only cards that were created
        created_cards = [c for c in anki_cards if c.created]

        # List of card lists. Cards inside the same card list come from the same
        # markdown file.
        cards_by_file: list[list[AnkiCard]] = []

        # Sort them by their path, this is needed for groupby to work correctly.
        created_cards = sorted(created_cards, key=lambda c: c.note_src.path)

        for _, g in groupby(created_cards, key=lambda c: c.note_src.path):
            # g is a iterator, convert it into a list
            cards_by_file.append(list(g))

        for cards in cards_by_file:
            # Read the text from a common markdown file
            md_file = cards[0].note_src.path
            lines = md_file.read_text(encoding="utf-8").splitlines()

            # Sort the cards by their start position in descending order.
            cards.sort(key=lambda c: c.note_src.start, reverse=True)

            # Start inserting markers from the end of the file to the start.
            for card in cards:
                s = card.note_src.start
                # We are inserting a marker with one empty line above and below.
                # Also we need to retain the original line that is in the start
                # position.
                marker = ["", f"<!-- nanki_note_id:{card.id} -->", ""]

                # Slice assignment is used to insert a marker list into a list.
                lines[s:s] = marker

            # Write back the modified content
            md_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def to_add_note_api(self) -> dict:
        """Return dict required by the addNote API call."""
        model_name = (
            self.metadata.note_type_basic
            if self.card_type == CardType.Basic
            else self.metadata.note_type_cloze
        )
        d = {
            "note": {
                "deckName": self.metadata.deck_name,
                "modelName": model_name,
                "fields": self.fields,
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "all",
                    "duplicateScopeOptions": {
                        "deckName": self.metadata.deck_name,
                        "checkChildren": True,
                        "checkAllModels": True,
                    },
                },
            },
        }

        if self.metadata.tags:
            d["note"]["tags"] = self.metadata.tags

        return d

    def to_update_note_api(self) -> dict:
        """Return dict required by the updateNote API call."""
        d = {
            "note": {
                "id": self.id,
                "fields": self.fields,
            },
        }

        if self.metadata.tags:
            d["note"]["tags"] = self.metadata.tags

        return d


def _extract_fields_and_id_from_card_text(card_text: str) -> tuple[dict, int | None]:
    """Process a card in markdown to HTML.

    Two steps are done here:

    1. Each card (string) is converted into a dict, where keys are names of the card
       fields (exactly the fields that appear in note types in Anki) and values are the
       text in fields themselves.
    2. Text in each field gets converted into html eqvivalent.

    """
    card_fields, card_id = _extract_card_fields_and_id(card_text)
    card_fields = card_fields_to_html_text(card_fields)

    return card_fields, card_id


def _extract_card_fields_and_id(text: str) -> tuple[dict, int | None]:  # noqa: C901, PLR0912
    """From given markdown text extract card fields with their values plus the card id.

    Fields are exactly the fields of the Note types in Anki.

    If Card id isn't set, that means that the card wasn't yet uploaded to the
    Anki. Card id is hidden in a markdown comment, which should be the first line in the
    stripped text, such as:

    <!-- nanki_note_id:1230123 -->
    """
    card_id = None
    id_pattern = r"<!-- nanki_note_id:(\d+) -->"
    lvl2_pattern = r"^##\s+(.+)$"

    lines = text.strip().splitlines()

    # Due to the strip, nanki_card_id can only appear on the first line
    m = re.search(id_pattern, lines[0])

    if m:
        card_id = int(m.group(1))

        # Only marker should be found in a line, with no preceding or trailing text.
        if m.group(0) != lines[0]:
            msg = "The line that id marker appears in has extra text, remove it."
            raise CardError(msg)

        # If card id is set then only empty lines can be between it and lvl2 header.
        for pos, line in enumerate(lines):
            if re.match(lvl2_pattern, line):
                if "\n".join(lines[1:pos]).strip():
                    msg = (
                        "Lines between nanki_note_id marker and first level 2 "
                        "header are not empty."
                    )
                    raise CardError(msg)
                break
    else:
        # If card id isn't set then the first line can only be lvl2 header with field.
        m = re.match(lvl2_pattern, lines[0])
        if not m:
            msg = "Card doesn't start with a level 2 header with a field."
            raise CardError(msg)

    # A little bit of text processing. Find locations of all valid level 2 header and
    # their fields. Then find lines between those fields and save them as values of the
    # fields.
    fields_with_pos = []
    for pos, line in enumerate(lines):
        if line.startswith("##"):
            m = re.match(lvl2_pattern, line)
            if not m:
                msg = "A level 2 header without label has been found."
                raise CardError(msg)

            field = m.group(1)
            fields_with_pos.append((field, pos))

    if not fields_with_pos:
        msg = "No level 2 headers were found"
        raise CardError(msg)

    card_fields = {}
    for idx, field_with_pos in enumerate(fields_with_pos):
        field, pos = field_with_pos

        if idx < len(fields_with_pos) - 1:
            next_pos = fields_with_pos[idx + 1][1]
            text_body = lines[pos + 1 : next_pos]
        else:
            text_body = lines[pos + 1 :]

        if not text_body:
            msg = "A level 2 header without text has been found."
            raise CardError(msg)

        card_fields[field] = "\n".join(text_body).strip()

    return card_fields, card_id
