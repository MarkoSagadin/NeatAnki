import prompt_toolkit
from prompt_toolkit.layout.processors import Processor, Transformation
from prompt_toolkit.styles import Style


class DefaultDimProcessor(Processor):
    def __init__(self, default_text: str):
        self.default_text = default_text

    def apply_transformation(self, ti):  # noqa: ANN201 ANN001
        """Make default text dim."""
        text = ti.document.text

        # if unchanged (still default), show dimmed
        if text == self.default_text:
            return Transformation([("class:default", text)])

        # otherwise normal rendering
        return Transformation(ti.fragments)


def prompt(question: str, *, default: str = "") -> str:
    """Ask a question.

    If default is given it will be dim and bold.
    """
    style = Style.from_dict(
        {
            "": "#ffffff",  # normal input
            "default": "ansigray bold",  # dimmed bold default
        },
    )

    return prompt_toolkit.prompt(
        question,
        default=default,
        style=style,
        input_processors=[DefaultDimProcessor(default)],
    )
