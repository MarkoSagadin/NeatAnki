import logging
import re
from dataclasses import dataclass
from pathlib import Path
from re import Match
from typing import Any, Self

from nanki.modules.ankicard import AnkiCard
from nanki.modules.filedata import FileData

log = logging.getLogger(__name__)


@dataclass
class TestFile(FileData):
    @classmethod
    def from_cards_and_html_templates(
        cls,
        cards: list[AnkiCard],
        templates: list[FileData],
        css: str | None,
        script: str | None,
    ) -> list[Self]:
        """Create various test files.

        There are several kinds of test files:
        - anki cards that were injected into templates
        - css file
        - script file

        They are all handled here because if css or script files are given, then
        injected anki cards need to know their location as they will reference them.
        """
        test_files = []

        for idx, card in enumerate(cards):
            for template in templates:
                template_fields = _get_all_fields_from_template(template.content)

                if not template_fields:
                    msg = (
                        f"\nNo fields were found in the following template file:"
                        f"\n\n\t{template.path}\n\n"
                        "(see card above)"
                    )
                    raise UserWarning(msg)

                # Replace {{Tags}} with the string of tags. If Anki card has no tags
                # expand to empty string
                if "Tags" in template_fields:
                    tags = " ".join(card.metadata.tags)
                    template.content = template.content.replace("{{Tags}}", tags)

                    # Remove the Tags, so all_template_fields_found_in_all_card_fields
                    # doesn't skip the card.
                    template_fields.remove("Tags")

                if not all_template_fields_found_in_all_card_fields(
                    card.fields,
                    template_fields,
                ):
                    continue

                content = _inject_card_fields_into_template(
                    card.fields,
                    template.content,
                )
                path = Path(template.path.stem) / f"card_{idx}.html"

                if css:
                    content, css_file = _add_css(content, css)
                    test_files.append(css_file)

                if script:
                    content, script_file = _add_js_script(content, script)
                    test_files.append(script_file)

                test_files.append(cls(path, content))

        return test_files


def _add_css(content: str, css: str) -> tuple[str, TestFile]:
    """Add css stylesheet link to the html content.

    Two cases needs to be handled:
    - html already has a stylesheet tag, in this case we only need to update href.
    - html doesn't have any stylesheet tag, in this case we add it
    """
    pattern = r'<link.*rel.*=.*"stylesheet".*href.*=.*"(.*)".*\/>'

    m = re.search(pattern, content)

    css_path: Path = Path(css)

    if m:
        old = m.group(1)
        new = str(Path("..") / css_path.name)
        # Ended up here
        content = content.replace(old, new)
    else:
        pos = content.find("</head>")
        link = f'<link rel="stylesheet" href="{css_path.name}" />'
        content = content[:pos] + link + content[pos:]

    css_file = TestFile.from_path(css_path)

    css_file.path = Path(css_file.path.name)

    return content, css_file


def _add_js_script(content: str, script: str) -> tuple[str, TestFile]:
    """Add js script link to the html content.

    Very similar to the above _add_css function.
    """
    pattern = r'<script.*src.*=.*"(.*)".*>'

    m = re.search(pattern, content)

    script_path: Path = Path(script)

    if m:
        old = m.group(1)
        new = str(Path("..") / script_path.name)
        # Ended up here
        content = content.replace(old, new)
    else:
        pos = content.find("</head>")
        link = f'<script src="{script_path.name}" />'
        content = content[:pos] + link + content[pos:]

    script_file = TestFile.from_path(script_path)

    script_file.path = Path(script_file.path.name)

    return content, script_file


def _inject_card_fields_into_template(fields: dict, template: str) -> str:
    """Inject card fields into the card template.

    Templates are expected to be valid HTML files. The replacement syntax goes like
    this:

    If HTML template has below content:

    ```
    {{Front}}
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
    pattern = re.compile(r"\{\{([\w\s]+)\}\}")

    def replace_field(m: Match[str]) -> str:
        # m.group(0) is the whole matched word, like "{{Front}}"
        # m.group(1) is just the "Front"
        field = m.group(1)
        # Replace with field's text, if field exists in the card
        return fields.get(field, m.group(0))

    return pattern.sub(replace_field, template)


def all_template_fields_found_in_all_card_fields(
    card_fields: dict,
    template_fields: list[str],
) -> bool:
    return set(template_fields).issubset(set(card_fields.keys()))


def _get_all_fields_from_template(template: str) -> list[Any]:
    return re.findall(r"\{\{([\w\s]+)\}\}", template)
