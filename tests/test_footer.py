"""Tests for footer hotkey display."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Input, Static

from syren.app import (
    FOOTER_HOTKEYS,
    FOOTER_PALETTE_HOTKEY,
    HotkeyFooter,
    RenameApp,
    footer_hotkey_markup,
    footer_palette_hotkey_markup,
    footer_primary_hotkey_markup,
)


def test_footer_hotkeys_include_filter() -> None:
    keys = [key for key, _label in FOOTER_HOTKEYS]
    assert keys == ["a", "f", "e", "q"]


def test_footer_hotkey_markup_includes_filter_key() -> None:
    markup = footer_hotkey_markup()
    assert " f " in markup
    assert "Focus filter" in markup


def test_footer_palette_hotkey_markup_uses_ctrl_p_display() -> None:
    markup = footer_palette_hotkey_markup()
    assert "^p" in markup
    assert "Palette" in markup
    assert FOOTER_PALETTE_HOTKEY == ("ctrl+p", "Palette")


def test_footer_shows_execute_binding() -> None:
    visible_actions = {binding.action for binding in RenameApp.BINDINGS if binding.show}
    assert "execute_rename" in visible_actions


def test_footer_shows_filter_binding() -> None:
    visible_actions = {binding.action for binding in RenameApp.BINDINGS if binding.show}
    assert "focus_filter" in visible_actions


def test_hotkey_footer_shows_filter_when_filter_focused(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test(size=(120, 40)) as pilot:
            filter_input = app.query_one("#file-filter", Input)
            filter_input.focus()
            await pilot.pause()

            primary = app.query_one("#hotkey-footer-primary", Static)
            assert " f " in primary.content
            assert "Focus filter" in primary.content

    asyncio.run(scenario())


def test_hotkey_footer_palette_is_right_aligned(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()

            footer = app.query_one(HotkeyFooter)
            primary = app.query_one("#hotkey-footer-primary", Static)
            palette = app.query_one("#hotkey-footer-palette", Static)

            assert "^p" in palette.content
            assert "Palette" in palette.content
            assert " f " in primary.content
            assert palette.region.x > primary.region.x
            assert palette.region.x + palette.region.width <= footer.region.width

    asyncio.run(scenario())
