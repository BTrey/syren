"""Tests for focus handling in the TUI."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Input, Select

from syren.app import RenameApp
from syren.transforms.sub_regex import SubRegexTransform


def test_escape_blurs_focused_filter_input(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test() as pilot:
            filter_input = app.query_one("#file-filter", Input)
            filter_input.focus()
            await pilot.pause()
            assert app.focused is filter_input

            await pilot.press("escape")
            await pilot.pause()
            assert app.focused is None

    asyncio.run(scenario())


def test_escape_blurs_focused_transform_field(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        app.transforms.append(SubRegexTransform())
        async with app.run_test() as pilot:
            app.refresh_transform_panels()
            await pilot.pause()
            field = app.query(Input).first()
            field.focus()
            await pilot.pause()
            assert app.focused is field

            await pilot.press("escape")
            await pilot.pause()
            assert app.focused is None

    asyncio.run(scenario())


def test_escape_without_focus_is_noop(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test() as pilot:
            app.set_focus(None)
            await pilot.pause()
            assert app.focused is None

            await pilot.press("escape")
            await pilot.pause()
            assert app.focused is None

    asyncio.run(scenario())


def test_select_field_is_blurrable(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        app.transforms.append(SubRegexTransform())
        async with app.run_test() as pilot:
            app.refresh_transform_panels()
            await pilot.pause()
            selects = app.query(Select)
            if not selects:
                return
            select = selects.first()
            select.focus()
            await pilot.pause()
            assert app.focused is select

            await pilot.press("escape")
            await pilot.pause()
            assert app.focused is None

    asyncio.run(scenario())


def test_escape_closes_add_transform_menu(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test() as pilot:
            app.set_focus(None)
            await pilot.pause()
            await pilot.press("a")
            await pilot.pause()
            assert len(app.screen_stack) > 1

            await pilot.press("escape")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    asyncio.run(scenario())
