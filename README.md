# renfield

Three-column TUI (Textual + Rich) for previewing chained filename transforms before renaming. Uses the Solarized Dark palette.

## Layout

| Transforms | Files | Preview |
|------------|-------|---------|
| Ordered transform stack with editable fields | Filterable file list from the current directory | Result of applying all transforms to each file |

## Transforms

- **Prepend** — text field; `#01` (or `#001`, etc.) auto-increments per file, preserving leading zeros
- **Postpend** — same numbering behavior, appended to the end
- **Replace** — literal find/replace
- **Sub Regex** — regex find/replace
- **Case** — UPPER, lower, or sentence case on the filename stem

Each transform is a Python class implementing `Transform.apply(filename, file_index)`. Add new transforms by subclassing `Transform`, registering with `register_transform`, and they appear in the add menu automatically.

## Hotkeys

- **a** — add a transform
- **Ctrl+↑ / Ctrl+↓** — move the selected transform up or down (click a transform panel to select it)
- **f** — focus the file filter
- **s** — toggle include subdirectories
- **q** — quit

The file filter accepts globs (`*.txt`) or fuzzy subsequence text.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- A terminal with TTY support

## Project layout

```
renfield/
  main.py              # root entry point
  pyproject.toml
  uv.lock
  src/renfield/        # application package
  tests/               # pytest suite
```

## Setup

```bash
cd ~/dev/playspace/renfield
uv sync --group dev
```

## Run

Run from a normal terminal (Textual needs a real TTY):

```bash
uv run renfield
uv run python main.py
```

## Development

```bash
uv run pytest
uv run pytest --cov=renfield --cov-report=term-missing
uv run mypy
uv run pylint src/renfield tests main.py
```
