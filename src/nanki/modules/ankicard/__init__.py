import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from nanki.modules.ankicard.helpers import extract_card_fields, extract_cards
from nanki.modules.ankicard.process_card.compile import card_fields_to_html_text
from nanki.modules.ankicard.process_card.format.wrappers import wrap_card_body
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

    @classmethod
    def from_markdown_files(cls, mds: list[MarkdownFile]) -> list["AnkiCard"]:
        """Create Anki Cards from Markdown files."""

        def flatten(xss: list[Any]) -> list[Any]:
            return [x for xs in xss for x in xs]

        return flatten([cls.from_markdown_file(md) for md in mds])

    @classmethod
    def from_markdown_file(cls, md: MarkdownFile) -> list["AnkiCard"]:
        """Create Anki Cards from a single Markdown file."""
        card_texts = extract_cards(md.content)

        cards = []
        try:
            for card_text in card_texts:
                if are_clozes_in_card(card_text):
                    clozes_handler = HandleClozes(card_text)
                    card_fields = _extract_fields_from_card_text(
                        clozes_handler.hashed_markdown,
                    )
                    card_fields = clozes_handler.inject_clozes(card_fields)
                    card = cls(md.metadata, card_fields, CardType.Cloze)
                else:
                    card_fields = _extract_fields_from_card_text(card_text)
                    card = cls(md.metadata, card_fields, CardType.Basic)

                cards.append(card)

        except CardError as error:
            # TODO: adjust the final error message
            log.info(
                f"\n📔 This is the card that created the error:📔\n{card_text}\n\n"
                "(see card above)",
            )
            log.error(error)
            raise

        return cards

    def to_api(self) -> dict:
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


def _extract_fields_from_card_text(card_text: str) -> dict:
    """Process a card in markdown to HTML.

    Two steps are done here:

    1. Each card (string) is converted into a dict, where keys are names of the card
       fields (exactly the fields that apper in note types in Anki) and values are the
       text in fields themselves.
    2. Text in each field gets converted into html eqvivalent.

    """
    card_fields = extract_card_fields(card_text)
    card_fields = card_fields_to_html_text(card_fields)

    return {field: wrap_card_body(text) for (field, text) in card_fields.items()}
