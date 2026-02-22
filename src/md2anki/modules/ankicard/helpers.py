import logging
import re

from md2anki.modules.ankicard.utils.card_error import CardError

logger = logging.getLogger(__name__)


def extract_cards(text: str) -> list[str]:
    """Extract cards from the given text, by splitting
    it at each occurrence of the markdown hr (only with -).
    Return a list of what is between the hrs, after it has
    been stripped.
    """
    regex_pattern = r"(?m)^(?:---+?)$"  # Match hr in markdown

    cards = re.split(regex_pattern, text)

    # Remove empty cards
    return [card.strip() for card in cards if card.strip()]


def extract_card_fields(text: str) -> dict:
    """From given markdown text extract card fields with their values.

    Fields are exactly the fields of the Note types in Anki.
    """
    lines = text.splitlines()

    # Start with two ##, followed by atleast one space, capture that text.
    pattern = r"^##\s+(.+)$"
    m = re.match(pattern, lines[0])

    if not m:
        msg = "Card doesn't start with a level 2 header with a field."
        raise CardError(msg)

    # A little bit of text processing. Find locations of all valid level 2 header and
    # their fields.
    # Then find lines between those fields and save them as values of the fields.

    fields_with_pos = []
    for pos, line in enumerate(lines):
        if line.startswith("##"):
            m = re.match(pattern, line)
            if not m:
                msg = "A level 2 header without label has been found."
                raise CardError(msg)

            field = m.group(1)
            fields_with_pos.append((field, pos))

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

    return card_fields
