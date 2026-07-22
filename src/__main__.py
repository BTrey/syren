"""Textual TUI for batch file renaming."""

from __future__ import annotations

from pathlib import Path

from .app import RenameApp, run


def main() -> int:
    """Run the syren TUI in the current working directory."""
    directory = Path.cwd()
    app = RenameApp(directory)
    app.run()
    return 0


__all__ = ["RenameApp", "main", "run"]
