<!-- prettier-ignore-start -->
<!-- omit in toc -->
# Developing Neat Anki
<!-- prettier-ignore-end -->

<!-- prettier-ignore-start -->
<!-- omit in toc -->
## Table of Contents
<!-- prettier-ignore-end -->

<!-- vim-markdown-toc GFM -->

- [Python setup](#python-setup)
- [Running the tool](#running-the-tool)
- [Running tests](#running-tests)
  - [Known issues](#known-issues)
    - [Editable install does not work](#editable-install-does-not-work)
- [JS/Sass setup](#jssass-setup)
- [prek (pre-commit)](#prek-pre-commit)

<!-- vim-markdown-toc -->

## Python setup

To develop and test `nanki` use [uv](https://docs.astral.sh/uv/) package and
project manager.

1. Install `uv`: https://docs.astral.sh/uv/getting-started/installation/
2. Open terminal in project root directory and run `uv sync`.

The command will install correct version of Python, `nanki`, it's dependencies
and will create a virtual environment in `.venv`.

## Running the tool

Simply run `uv run nanki` to test and develop the tool. By default the `uv`
installs `nanki` in editable mode, which means that any code changes are
immediately seen in invoked tool.

## Running tests

To execute tests run `uv run pytest`.

### Known issues

#### Editable install does not work

If `make install` or `make install-dev` (more exactly `pip install -e .`) ever
misbehaves, it is probably due to this:
<https://github.com/pypa/pip/issues/7953>.

Run the below command once and then again `make install`, this fixed it last
time:

```bash
python3 -m pip install --prefix=$(python3 -m site --user-base) -e .
```

## JS/Sass setup

See documentation in [frontend folder](../frontend/README.md).

## prek (pre-commit)

When committing code is mandatory that `prek` tool is installed.

1. Install `prek` tool: <https://github.com/j178/prek>
2. Run `prek install` inside this repo.

Last step is always needed if repo was cleanly cloned.

`prek` will now run automatically on every commit. To run it manually on all
staged files run `prek run`. To run to on all files in the project run
`prek run --all-files`.
