import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from nanki.modules.ankicard import AnkiCard
from nanki.modules.ankicard.helpers import (
    get_all_fields_from_template,
    inject_card_fields_into_template,
)
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
            test_files = []
            for template in templates:
                template_fields = get_all_fields_from_template(template.content)

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

                    # Remove the Tags, so _all_template_fields_found_in_all_card_fields
                    # doesn't skip the card.
                    template_fields.remove("Tags")

                if not _all_template_fields_found_in_all_card_fields(
                    card.fields,
                    template_fields,
                ):
                    continue

                content = inject_card_fields_into_template(
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

            # If the set of card fields is bigger than every set of template fields then
            # that means that user created a card that can't be matched to any html
            # template.
            all_t_fields = [get_all_fields_from_template(t.content) for t in templates]
            num_card_fields = len(set(card.fields.keys()))

            if all(num_card_fields > len(set(t_field)) for t_field in all_t_fields):
                msg = "Fields in the parsed card don't match any found html template!"
                raise UserWarning(msg)

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


def _all_template_fields_found_in_all_card_fields(
    card_fields: dict,
    template_fields: list[str],
) -> bool:
    return set(template_fields).issubset(set(card_fields.keys()))
