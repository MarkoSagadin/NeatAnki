# TODO notes

## What can be done with the processed cards

At this point you have processed card data, depending on the provided flag,
specific command, etc., you can do something different with this.

Options:

1. directly upload to Anki via Ankiconnect. This is the main usecase.
2. Output as raw files. for this you need some kind of naming scheme, like
   card_1_front.html, card_1_back.html, card_2_front.html, card_2_back.html,
   etc. I am not sure if I can argument what would be the purpose for this, but
   it seems basic.
3. Provide a html template on the cmd line, embed cards into it. With that I
   will generate html files that I can open directly in the Firefox and see what
   is going on with the output. See "Card Templates" section.

## Card templates

So this should be almost valid HTML file with special markers into which I can
do text replacement.

The syntax for replacement will be the same as for the Anki's card templates.

Specifically:

- `{{Front}}` will be replaced by the text in the "Front" field of the card.
- There are special, reserved fields:
  - Tags
  - Type
  - Deck
  - Subdeck
  - CardFlag
  - Card
  - FrontSide

User can provide prefix or folder name for the Card template. I will scan for
the files that match such prefix and try to apply processed cards to those file.

<https://docs.ankiweb.net/templates/fields.html>

## Differentiating between different note types

Currently I have:

- note_type_basic: str
- note_type_cloze: str

which someone can write to frontmatter.

Right now only the presence of the clozes in the markdown text decides that the
card should use note_type_cloze, but everything else is clumped up in the
note_type_basic.

What if you want mix basic type with some special one like the one that has 5
fields...

maybe something like this (instruction to the user: list all note types that you
would like to use): notetype: "some name for basic" "some name for cloze" "some
name for third note type"

then the code needs to check what fields each note type expects, each card's
field names are then inspected and matched to the note type.

If they can't be matched then error is raised. Also, error must be raised if
note types have identical number of fields and identical field names (you can't
then do matching.)

**EDIT**: Can fields be optional??? That might complicate above logic.

## Frontmatter

As I was writing above section I thought of a good question: If I plan at some
point to introduce a global config, something like ~/.config/nanki/config.toml,
which could have global settings, I might not need to write frontmatter in every
file. From user perspective it is easier to set values once and not keep writing
them in every single file.

If you do that then you have to figure out filtering, right know a valid
frontmatter structure is mandatory for the markdown file to be considered for
card extraction.

If file don't has frontmatter then you can:

- check if if it only has level 2 headers (why aren't level 1 headers allowed
  again???), if not bail
- try to split file by `---` markers, but this isn't really telling me anything
- then try to convert each raw card into card fields.

I guess I can convert every markdown file...

## AnkiCard class

It doesn't need entire metadata member only few things (most important only one
note type).

## Tasks

- Card templates seem to be implemented ok. You still need to check for the
  special reserved fields, but that is fine for now.
- Clean up user interface and error handling. This will be a big task so you
  want to do this at some point when you will have sufficient functionality.
- Add prints to the top level that will say how many cards were found and also
  if none were found
- The text fields given in the markdown have to match the chosen note type. So
  before you start uploading card you need to verify that all cards that you
  will upload match the expected note type.
- Update the binary name to `nanki`, this will require changes in
  pyproject.toml, and file structure.
- Add documentation for card-body css file
- md2anki_out build dir should be cleaned everytime.
- Tags fields also need to be substituted in the python code, currently they
  aren't
- Add support for images in the markdown files.

## Milestones

- 1st milestone: End-to-End functionality. I can convert and upload cards.
  Uploading themes and html decks is not yet possible. Clozes are expected to
  look ugly. You don't need to yet have the frontend folder.
  - This was DONE.
- 2nd milestone: add frontend folder, use bun to compile it. Clean up tab stuff,
  improve cloze cards.
  - This was DONE
- 3rd milestone: clean up the code and project structure. Clean up the cli
  interface, provide good help strings and log statements.
  - Code was cleaned up with Ruff

Open code session: <https://opncd.ai/share/nsPcYsOn>
