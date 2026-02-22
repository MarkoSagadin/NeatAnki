import logging
import re

from md2anki.modules.ankicard.utils.card_error import CardError
from md2anki.modules.ankicard.utils.debug_tools import expressive_debug

logger = logging.getLogger(__name__)


class HandleClozes:
    """This class takes care of hashing and unhashing clozes.
    This is necessary to make sure code-highlighting won't break clozes.
    """

    def __init__(self, card: str) -> None:
        self.card = card
        self._clozes = self._get_clozes(card)
        self._hash_dictionary = self._create_hash_dictionary(self._clozes)
        self.hashed_markdown = self._hash_clozes()

    def _get_clozes(self, text: str) -> list[str]:
        """Extract clozes from text.

        Pattern:
        {{c1::something}}
        {{C9::something}}
        """
        clozes_regex = re.compile(r"(?i)({{c\d+::.+?}})")

        return clozes_regex.findall(text)

    def _create_hash_dictionary(self, clozes: list[str]) -> dict[str, str]:
        """Create a hash dictionary.

        Transform matched clozes into a dictionary that has:
        keys: hashed match
        values: cloze
        """
        # A dictionary built to use with translate()
        # {key: ord(number), value: letter} + "-" : Z
        number_to_letter_translation = {
            48: "A",
            49: "B",
            50: "C",
            51: "D",
            52: "E",
            53: "F",
            54: "G",
            55: "H",
            56: "I",
            57: "J",
            45: "Z",
        }

        result = {}
        for cloze in clozes:
            hash_number = str(hash(cloze))

            hash_in_letters = hash_number.translate(number_to_letter_translation)
            result[hash_in_letters] = cloze

        return result

    def _replace_clozes_with_hashes(
        self,
        markdown_text: str,
        hashed_clozes: dict[str, str],
    ) -> str:
        """Replace the text of clozes ({{c1::This part}}) with it's hash."""
        if not hashed_clozes:
            return markdown_text

        markdown_with_hashes = markdown_text

        for hash_key, cloze in hashed_clozes.items():
            cloze_regex = re.compile(re.escape(cloze))
            markdown_with_hashes, number_of_substitutions = re.subn(
                cloze_regex,
                hash_key,
                markdown_with_hashes,
            )
            if number_of_substitutions < 1:
                msg = (
                    "Bad formatting in code's cloze; make sure you are not using "
                    "nested clozes."
                )
                raise CardError(msg)
        expressive_debug(logger, "Markdown with hash", markdown_with_hashes, "json")

        return markdown_with_hashes

    def _hash_clozes(self) -> str:
        """Replace clozes that are part of the card with string hashes."""
        return self._replace_clozes_with_hashes(
            self.card,
            self._hash_dictionary,
        )

    def inject_clozes(self, card_fields: dict[str, str]) -> dict[str, str]:
        """Replace the hashes in the text with the corresponding cloze:
        HSJDKASKHDAKS -> {{c1::my cloze}}
        And normalize clozes (make sure the "c" is lowercase).
        """
        for hashed_cloze, cloze in self._hash_dictionary.items():
            normalized_cloze = "{{c" + cloze[3:]
            hash_regex = re.compile(re.escape(hashed_cloze))

            card_fields = {
                field: re.sub(hash_regex, normalized_cloze, text)
                for (field, text) in card_fields.items()
            }

        return card_fields


def are_clozes_in_card(card: str) -> bool:
    """Check if in the card there is at least one cloze.

    Pattern:
    {{c1::something}}
    {{C5::something else}}
    """
    clozes_regex = re.compile(r"{{c(\d+)::(.+?)}}", re.IGNORECASE)

    return bool(clozes_regex.search(card))
