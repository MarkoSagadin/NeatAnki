import logging
import shutil as sh
import sys
from pathlib import Path

import click

from nanki.modules.ankicard import AnkiCard
from nanki.modules.ankiconnect import AnkiConnect
from nanki.modules.filedata import FileData
from nanki.modules.markdownfile import MarkdownFile
from nanki.modules.testfile import TestFile

logger = logging.getLogger(__name__)


@click.command
@click.option(
    "-t",
    "--template-prefix",
    required=True,
    help=(
        "Prefix used to select HTML templates. "
        "All files starting with this prefix are used. "
        "Example: '-t web_' matches 'web_basic.html' and 'web_cloze.html'."
    ),
)
@click.option(
    "-c",
    "--css",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to CSS file.",
)
@click.option(
    "-s",
    "--script",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to JavaScript file.",
)
@click.argument(
    "path",
    nargs=1,
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "-o",
    "--output-dir",
    default="nanki_out",
    help="Path to output directory, default: nanki_out",
)
def test(
    template_prefix: str,
    path: str,
    css: str,
    script: str,
    output_dir: str,
) -> None:
    """Convert Nanki Markdown files to HTML files.

    PATH can point to a Nanki Markdown file or a directory.

    If PATH is a file, only that file is converted.
    If PATH is a directory, it is searched recursively and all found Nanki Markdown
    files are converted.

    During conversion Nanki cards are extracted from all files. Each Nanki card is
    checked, if it fits one of the html files, provided by the --template-prefix. If
    it does, then that card is converted into a HTML file, if it doesn't, it is
    not converted.

    If paths to CSS file or JS script are given, then those are injected into generated
    HTML files.

    Generated HTML files are by default created in the nanki_out directory. Use web
    browser to open them for visual inspection.
    """
    try:
        md_files = MarkdownFile.load_files(path)
    except ValueError as e:
        logger.error(f"😯 An error occurred when trying to open the input md file: {e}")
        sys.exit(1)

    # TODO add exception handling
    anki_cards = AnkiCard.from_markdown_files(md_files)

    template_paths = sorted(Path.cwd().glob(f"{template_prefix}*"))
    templates = [FileData.from_path(t) for t in template_paths]

    test_files = TestFile.from_cards_and_html_templates(
        anki_cards,
        templates,
        css,
        script,
    )

    sh.rmtree(output_dir, ignore_errors=True)

    out_path = Path.cwd() / Path(output_dir)

    for test_file in test_files:
        test_file.write(out_path)


@click.command
@click.argument(
    "path",
    nargs=1,
    type=click.Path(exists=True),
    required=True,
    # help="Path to scan for markdown files", TODO: add help somewhere
)
def run(path: str) -> None:
    """Convert markdown files to Anki cards and upload them to Anki."""
    try:
        md_files = MarkdownFile.load_files(path)
    except ValueError as e:
        logger.error(f"😯 An error occurred when trying to open the input md file: {e}")
        sys.exit(1)

    # TODO add exception handling
    anki_cards = AnkiCard.from_markdown_files(md_files)

    try:
        conn = AnkiConnect()
    except UserWarning as e:
        logger.error(f"😯 An error occurred when trying to connect to Anki: {e}")
        sys.exit(1)

    conn.upload_cards(anki_cards)


# @click.command
# @click.option("-t", "--template_prefix", help="Html template prefix")
# @click.argument("path", nargs=1, type=click.Path(), required=True)
# def run(path: str, template_prefix: str):
#     """This command converts."""
#
#     try:
#         markdown_handle = MarkdownHandler(path)
#     except Exception as error:
#         logger.info("😯 An error occurred when trying to open the input md file:")
#         logger.error(error)
#         sys.exit(1)
#     # expressive_debug(
#     #     logger,
#     #     "Markdown input file frontmatter",
#     #     markdown_handle.metadata,
#     #     "json",
#     # )
#
#     # print(markdown_handle.content)
#
#     # Next things to implement.
#     # Commented options should be removed
#     obsdian_vault = " "
#     image_dir = "/home/skobec/Programs/nanki/input_images"
#     try:
#         cards_with_info = markdown_to_anki(
#             markdown_handle.content,
#             vault=obsdian_vault,
#             linenos=True,  # maybe keep
#             scrollable_code=True,  # default yes
#             no_tabs=True,  # new default
#             interactive=True,  # new default
#             # Whether to keep processing if error is detected.
#             # This should be false, fail as soon as bad card is detected.
#             fast_forward=False,
#             images_dir=image_dir,  # Remove
#             folders_to_exclude="",  # This should be a configurable option, it think
#         )
#     except CardError as error:
#         # TODO: make this exception more concrete if needed
#         logger.info(
#             "\n😯 There was an error and no file was created.\n"
#             "Exited with the following error:"
#         )
#         logger.error(error)
#         print("ERROR")
#         sys.exit(1)
#
#     template_paths = sorted(Path.cwd().glob(f"{template_prefix}*"))
#     templates = [FileData.from_path(t) for t in template_paths]
#
#     # print(cards_with_info["cards"])
#
#     injected_cards = inject_cards_into_templates(cards_with_info["cards"], templates)
#
#     for injected_card in injected_cards:
#         injected_card.write(Path.cwd() / Path("output_dir"))


@click.group()
def cli() -> None:
    """This is a markdown to anki converter."""


cli.add_command(run)
cli.add_command(test)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
