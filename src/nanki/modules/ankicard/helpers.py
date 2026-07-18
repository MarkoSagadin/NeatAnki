import logging
import re
from re import Match

logger = logging.getLogger(__name__)


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
