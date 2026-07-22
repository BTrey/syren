"""Solarized Dark palette for the rename TUI."""

from __future__ import annotations

# Solarized Dark (Ethan Schoonover)
SOLARIZED = {
    "base03": "#002b36",
    "base02": "#073642",
    "base01": "#586e75",
    "base00": "#657b83",
    "base0": "#839496",
    "base1": "#93a1a1",
    "base2": "#eee8d5",
    "base3": "#fdf6e3",
    "yellow": "#b58900",
    "orange": "#cb4b16",
    "red": "#dc322f",
    "magenta": "#d33682",
    "violet": "#6c71c4",
    "blue": "#268bd2",
    "cyan": "#2aa198",
    "green": "#859900",
}

SOLARIZED_CSS = """
Screen {
    background: #002b36;
    color: #839496;
}

Header {
    background: #073642;
    color: #93a1a1;
    dock: top;
    height: 1;
}

Footer {
    background: #073642;
    color: #586e75;
    dock: bottom;
    height: 1;
}

.column {
    border: solid #586e75;
    height: 1fr;
    padding: 0 1;
}

.column-title {
    background: #073642;
    color: #268bd2;
    text-style: bold;
    width: 1fr;
    content-align: center middle;
    height: 1;
    margin-bottom: 1;
}

.filter-panel {
    border: solid #2aa198;
    height: auto;
    padding: 0 1;
    margin-bottom: 1;
}

.filter-panel Label {
    color: #93a1a1;
}

.filter-panel Input {
    background: #073642;
    border: tall #586e75;
    color: #eee8d5;
    margin: 0 0 1 0;
}

.filter-panel Checkbox {
    background: #002b36;
    color: #839496;
}

FileList, PreviewList {
    height: 1fr;
    background: #002b36;
    scrollbar-background: #073642;
    scrollbar-color: #586e75;
}

FileList > ListItem, PreviewList > ListItem {
    padding: 0 1;
}

FileList > ListItem.-highlight, PreviewList > ListItem.-highlight {
    background: #073642;
    color: #eee8d5;
}

TransformList {
    height: 1fr;
    overflow-y: auto;
    scrollbar-background: #073642;
    scrollbar-color: #586e75;
}

TransformPanel {
    border: solid #586e75;
    height: auto;
    padding: 0 1;
    margin-bottom: 1;
    background: #002b36;
}

TransformPanel.-selected {
    border: solid #268bd2;
    background: #073642;
}

TransformPanel .transform-name {
    color: #b58900;
    text-style: bold;
    height: 1;
    margin-bottom: 1;
}

TransformPanel Input {
    background: #073642;
    border: tall #586e75;
    color: #eee8d5;
    margin-bottom: 1;
}

TransformPanel Select {
    background: #073642;
    border: tall #586e75;
    color: #eee8d5;
    margin-bottom: 1;
}

TransformPanel Label {
    color: #93a1a1;
    margin-bottom: 0;
}

AddTransformMenu {
    align: center middle;
}

AddTransformMenu OptionList {
    width: 40;
    height: auto;
    max-height: 14;
    border: solid #268bd2;
    background: #073642;
    padding: 1;
}

AddTransformMenu OptionList > .option-list--option-highlight {
    background: #268bd2;
    color: #fdf6e3;
}
"""
