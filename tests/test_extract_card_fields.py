import pytest

from nanki.modules.ankicard import CardError, _extract_card_fields_and_id

note = """## Front

Front text

## Back

Back text
"""

note_with_space = """
## Front

Front text

## Back

Back text
"""

note_no_space = """## Front
Front text
## Back
Back text
"""


@pytest.mark.parametrize("text", [note, note_with_space, note_no_space])
def test_create_a_single_note(text: str) -> None:

    expected_fields = {"Front": "Front text", "Back": "Back text"}

    fields, card_id = _extract_card_fields_and_id(text)

    assert card_id is None
    assert fields == expected_fields


note_with_id = """<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
"""

note_with_id_extra_space = """<!-- nanki_note_id:123 -->


## Front

Front text

## Back

Back text
"""

# Although we will be adding a single empty line above and below the id, it is okay if
# users delete them.
note_no_space_before_lvl2_header = """<!-- nanki_note_id:123 -->
## Front

Front text

## Back

Back text
"""


@pytest.mark.parametrize(
    "text",
    [
        note_with_id,
        note_with_id_extra_space,
        note_no_space_before_lvl2_header,
    ],
)
def test_create_a_single_note_with_id(text: str) -> None:

    fields, card_id = _extract_card_fields_and_id(text)

    expected_fields = {"Front": "Front text", "Back": "Back text"}

    assert card_id == 123
    assert fields == expected_fields


bad_note_text_before_lvl2_header = """asdsadassd
## Front

Front text

## Back

Back text
"""


def test_note_with_text_before_lvl2_header_fails() -> None:

    exp_msg = "Card doesn't start with a level 2 header with a field."
    with pytest.raises(CardError, match=exp_msg):
        _ = _extract_card_fields_and_id(bad_note_text_before_lvl2_header)


bad_note_text_between_id_and_lvl2_header = """<!-- nanki_note_id:123 -->
asdasd
## Front

Front text

## Back

Back text
"""


def test_note_with_text_between_id_and_lvl2_header_fails() -> None:

    exp_msg = (
        "Lines between nanki_note_id marker and first level 2 header are not empty."
    )
    with pytest.raises(CardError, match=exp_msg):
        _ = _extract_card_fields_and_id(bad_note_text_between_id_and_lvl2_header)


bad_note_no_headers_with_id = """<!-- nanki_note_id:123 -->
Front text

Back text
"""


def test_note_with_no_headers() -> None:

    exp_msg = "No level 2 headers were found"
    with pytest.raises(CardError, match=exp_msg):
        _ = _extract_card_fields_and_id(bad_note_no_headers_with_id)


note_with_id_with_trailing_text = """<!-- nanki_note_id:123 -->asdasd

## Front

Front text

## Back

Back text
"""

# TODO: for some reason below isn't detected by the regex
note_with_id_with_preceding_text = """asdasd<!-- nanki_note_id:123 -->

## Front

Front text

## Back

Back text
"""


@pytest.mark.parametrize(
    "text",
    [
        note_with_id_with_trailing_text,
        note_with_id_with_preceding_text,
    ],
)
def test_note_with_id_with_extra_text_fails(text: str) -> None:

    exp_msg = "The line that id marker appears in has extra text, remove it."
    with pytest.raises(CardError, match=exp_msg):
        _ = _extract_card_fields_and_id(text)
