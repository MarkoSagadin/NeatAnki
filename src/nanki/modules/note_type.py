from dataclasses import dataclass
from pathlib import Path

from nanki.modules.ankicard.helpers import get_all_fields_from_template


@dataclass
class NoteType:
    """Data class representing an Anki card."""

    model_name: str
    in_order_fields: list[str]
    css: str
    is_cloze: bool

    card_templates: dict[str, str]

    @classmethod
    def from_files(
        cls,
        name: str,
        html_templates: list[Path],
        css_file: Path,
        js_file: Path,
        *,
        is_cloze: bool = False,
    ) -> "NoteType":
        """Create Anki Cards from Markdown files."""
        card_templates = {}
        js = f"\n</script>\n{js_file.read_text().strip()}\n</script>"

        for h in html_templates:
            key = h.stem.split("-")[-1].replace("_", " ")
            # Append js script to the template
            card_templates[key] = h.read_text() + js

        in_order_fields = []
        for html_text in card_templates.values():
            in_order_fields += get_all_fields_from_template(html_text)

        in_order_fields = list(set(in_order_fields))

        return cls(
            name,
            in_order_fields,
            css_file.read_text(),
            is_cloze,
            card_templates,
        )

    def to_create_model_api(self) -> dict:
        """Return dict required by the createModel API call."""
        return {
            "modelName": self.model_name,
            "inOrderFields": self.in_order_fields,
            "css": self.css,
            "isCloze": self.is_cloze,
            "cardTemplates": [self.card_templates],
        }

    def to_update_model_api(self) -> dict:
        """Return dict required by the updateModelTemplates API call."""
        return {
            "model": {
                "name": self.model_name,
                "templates": {
                    "Card 1": self.card_templates,
                },
            },
        }
