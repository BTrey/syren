"""Tests for filter bar label styling."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Label

from syren.app import RenameApp
from syren.transforms import format_transform_menu_label


def test_filter_label_highlights_first_letter() -> None:
    assert format_transform_menu_label("Filter") == "[bold #b58900]F[/]ilter"


def test_filter_bar_uses_highlighted_label(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test() as pilot:
            await pilot.pause()
            label = app.query_one("#filter-bar Label", Label)
            assert label.content == format_transform_menu_label("Filter")

    asyncio.run(scenario())
