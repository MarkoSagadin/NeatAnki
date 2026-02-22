import contextlib
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .filedata import FileData

# NOTE: Keep MarkdownMetadata and metadata_schema in sync if changing.
metadata_schema = {
    "type": "object",
    "properties": {
        "deck_name": {"type": "string"},
        "note_type_basic": {"type": "string"},
        "note_type_cloze": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "deck_name",
        "note_type_basic",
        "note_type_cloze",
    ],
    "optional": ["tags", "no_tabs"],
    "additionalProperties": False,
}


@dataclass
class MarkdownMetadata:
    deck_name: str
    note_type_basic: str
    note_type_cloze: str

    # That is how you define a mutable default in dataclass
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_metadata(cls, metadata: dict) -> "MarkdownMetadata":
        """Validate given metadata against the schema and create an instance."""
        if not metadata:
            msg = "No metadata found in file."
            raise ValueError(msg)

        try:
            validate(instance=metadata, schema=metadata_schema)
        except ValidationError as e:
            msg = f"Invalid metadata schema: {e}"
            raise ValidationError(msg) from e

        tags = metadata.get("tags", [])

        # Add a default "nanki" tag
        metadata["tags"] = ["nanki", *tags]

        return cls(**metadata)


@dataclass
class MarkdownFile(FileData):
    # the content field contains only the markdown content, the frontmatter data is
    # validated and stored in the below metadata field.
    metadata: MarkdownMetadata

    @classmethod
    def load_files(cls, any_path: str | Path) -> list["MarkdownFile"]:
        """From given path create a list of MarkdownHandler objects.

        If any_path is a file, that file is validated and if successfully validated, a
        list with a single object is created.

        If any_path is a directory a recursive search is done. All markdown files are
        opened and validated. Ones that that are successfully validated are converted
        into MarkdownFile object, added to a list, which is returned.
        """
        path: Path = Path(any_path)

        if path.is_file():
            fd = FileData.from_path(path)

            metadata, content = frontmatter.parse(fd.content)
            metadata = MarkdownMetadata.from_metadata(metadata)

            return [cls(fd.path, content, metadata)]

        if path.is_dir():
            files = []
            for p in path.rglob("*.md"):
                with contextlib.suppress(ValueError, ValidationError):
                    files += cls.load_files(p)
            return files

        msg = "Invalid path was given, it isn't a file nor a directory."
        raise ValueError(msg)

    # TODO: remove it, when you are sure you don't need it.
    def get_frontmatter_text(self) -> str:
        """Return frontmatter text."""
        yaml_text = frontmatter.YAMLHandler().export(self.metadata)
        return "---\n" + yaml_text + "\n---\n\n"
