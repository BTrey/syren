# syren

Three-column TUI (Textual + Rich) for previewing chained filename transforms before renaming. Uses the Solarized Dark palette.

## Layout

| Transforms | Files | Preview |
|------------|-------|---------|
| Ordered transform stack with editable fields | Filterable file list from the current directory | Result of applying all transforms to each file |

A bordered filter row above the columns holds the filename filter, the include-subdirectories checkbox, the include-hidden-files checkbox, and the ignore-extension checkbox.

By default the last "." in a filename marks the extension. Transforms apply only to the base name and the engine keeps the extension. Select **Ignore extension** to apply transforms to the whole filename instead.

## Transforms

- **Prepend** — text field; `#01` (or `#001`, etc.) auto-increments per file, preserving leading zeros
- **Postpend** — same numbering behavior, appended to the end
- **Replace** — literal find/replace
- **Sub Regex** — regex find/replace
- **Case** — UPPER, lower, Sentence, or Title Case on the filename stem

Each transform is a Python class implementing `Transform.apply(filename, file_index)`. Add new transforms by subclassing `Transform`, registering with `register_transform`, and they appear in the add menu automatically.

Each transform panel has an **X** button in the upper-right corner to remove it from the stack.

## Hotkeys

- **a** — add a transform
- **Ctrl+↑ / Ctrl+↓** — move the selected transform up or down (click a transform panel to select it)
- **f** — focus the file filter
- **s** — toggle include subdirectories
- **h** — toggle include hidden files
- **i** — toggle ignore extension
- **Esc** — remove focus from the current input/select field
- **e** — execute rename (with confirmation and collision checks)
- **q** — quit

The file filter accepts globs (`*.txt`) or fuzzy subsequence text.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- A terminal with TTY support

## Project layout

```
syren/
  main.py              # root entry point
  pyproject.toml
  uv.lock
  src/                 # application source (installed as the syren package)
    app.py
    colors.py
    engine.py
    files.py
    fuzzy.py
    transforms/
  tests/               # pytest suite
```

## Setup

```bash
cd ~/dev/playspace/syren
uv sync --group dev
```

## Run

Run from a normal terminal (Textual needs a real TTY):

```bash
uv run syren
uv run python main.py
```

## Development

```bash
uv run pytest
uv run pytest --cov=syren --cov-report=term-missing
uv run mypy
uv run pylint src tests main.py
```
