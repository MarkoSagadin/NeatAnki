import logging
import re
from re import Match

from nanki.modules.ankicard.utils.card_error import CardError

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


def inject_card_fields_into_template(fields: dict, template: str) -> str:
    """Inject card fields into the card template.

    Templates are expected to be valid HTML files. The replacement syntax goes like
    this:

    If HTML template has below content:

    ```
    {{Front}}
    ```

    or

    ```
    {{cloze:Front}}
    ```

    then everything is replaced by the value of the key in the card matching the text
    inside the curly braces. Replacement is done only once, for example, if "{{Front}}"
    is replaced with "{{Back}}", then this new string won't be replaced again, even if
    there is a match.

    That's basically it, there are some special fields though that need to be handled
    later.

    This behavior is the same as in the Anki:
    https://docs.ankiweb.net/templates/fields.html
    """
    basic_fields = re.compile(r"\{\{([\w\s]+)\}\}")
    cloze_fields = re.compile(r"\{\{cloze:([\w\s]+)\}\}")

    def replace_field(m: Match[str]) -> str:
        # m.group(0) is the whole matched word, like "{{Front}}"
        # m.group(1) is just the "Front"
        field = m.group(1)
        # Replace with field's text, if field exists in the card
        return fields.get(field, m.group(0))

    template = basic_fields.sub(replace_field, template)

    return cloze_fields.sub(replace_field, template)


def get_all_fields_from_template(template: str) -> list[str]:
    basic_fields = re.findall(r"\{\{([\w\s]+)\}\}", template)
    cloze_fields = re.findall(r"\{\{cloze:([\w\s]+)\}\}", template)
    return basic_fields + cloze_fields
