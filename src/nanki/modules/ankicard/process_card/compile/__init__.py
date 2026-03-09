import html
import logging
import re

import mistune
import pygments
import pygments.formatters.html
import pygments.lexers
import pygments.util

logger = logging.getLogger(__name__)


def card_fields_to_html_text(card_fields: dict) -> dict:
    """Convert card text fields to html text."""
    return {
        field: markdown_to_html_with_highlight(
            text,
            linenos=True,
            scrollable_code=True,
        )
        for field, text in card_fields.items()
    }


def markdown_to_html_with_highlight(
    text: str,
    *,
    linenos: bool = True,
    scrollable_code: bool = False,
) -> str:
    """Parse the text and compile to html.

    Code blocks are highlighted using
    a custom pygments template (see HighlightRenderer)
    """
    markdown = mistune.create_markdown(
        escape=False,
        hard_wrap=False,
        renderer=HighlightRenderer(linenos=linenos, scrollable_code=scrollable_code),
        plugins=[
            "strikethrough",
            "footnotes",
            "table",
            "url",
            "def_list",
        ],
    )

    return markdown(text)


class HighlightRenderer(mistune.HTMLRenderer):
    def __init__(
        self,
        *,
        linenos: bool = True,
        scrollable_code: bool = False,
    ):
        super().__init__(escape=True, allow_harmful_protocols=None)
        self.linenos = linenos
        self.scrollable_code = scrollable_code

    def block_code(self, code: str, info: str = "") -> str:
        """Handle block code."""
        try:
            lexer = pygments.lexers.get_lexer_by_name(info)
        except pygments.util.ClassNotFound:
            lexer = pygments.lexers.guess_lexer(code)

        code_class = "highlight__code"

        if self.scrollable_code:
            code_class += " highlight__code--scrollable-code"

        if self.linenos:
            code_class += " highlight--linenos"

        formatter = LineWrappingHtmlFormatter(
            cssclass=code_class,
            wrapcode=True,
            scrollable_code=self.scrollable_code,
        )

        # Clozes handling
        # TODO optimization: some steps can be avoided if there are no clozes
        highlighted_code = pygments.highlight(code, lexer, formatter)

        section_head = '<section class="highlight">'
        if self.linenos:
            section_head = '<section class="highlight highlight--linenos">'

        language_span = f'<span class="highlight__language">{lexer.name}</span>'

        return f"{section_head}{language_span}{highlighted_code.strip()}</section>"

    def image(self, src, alt="", title=None):  # noqa: ANN001, ANN201
        """Handle images."""
        # NOTE: Doesn't support title for now; can add if requested
        _ = title
        src = self._safe_url(src)
        alt = html.escape(alt)

        is_hyperlink = bool(re.match(r"https?://", src))

        if is_hyperlink:
            return f'<img src="{src}" alt={alt}>' if alt else f'<img src="{src}">'
        path_slash_regex = re.compile(r"[\\\/]")  # Support for multiple OSs
        last_word = re.split(path_slash_regex, src)[-1]
        return (
            f'<img src="{last_word}" alt={alt}>' if alt else f'<img src="{last_word}">'
        )


class LineWrappingHtmlFormatter(pygments.formatters.html.HtmlFormatter):
    def __init__(self, **options):
        # Override the default formatter to add new scrollable_code option.
        super().__init__(**options)
        self.scrollable_code = options.get("scrollable_code", False)

    # https://pygments.org/docs/formatters/#HtmlFormatter
    def wrap(self, source):  # noqa: ANN001, ANN201
        """Wrap the ``source``, which is a generator yielding
        individual lines, in custom generators. See docstring
        for `format`. Can be overridden.
        """
        output = source
        if self.wrapcode:
            output = self._wrap_code(output)

        output = self._wrap_lines(source)
        return self._wrap_pre(output)

    def _wrap_lines(self, source):  # noqa: ANN001, ANN202
        """Wrap each line in a span with the 'highlight__line' class."""
        line_class = "highlight__line"

        if self.scrollable_code:
            line_class += " highlight__line--scrollable-code"

        for line_number, line_text in source:
            wrapped_line = line_text
            if line_number == 1:
                # it's a line of formatted code
                wrapped_line = f"<span class='{line_class}'>{line_text}</span>"
            # FIXME: maybe? when line_number != 1; yield line_number, line_text?
            yield line_number, wrapped_line
