"""Tests for the add-transform menu helpers."""

from __future__ import annotations

import asyncio
from pathlib import Path

from syren.app import AddTransformScreen, RenameApp
from syren.transforms import (
    format_transform_menu_label,
    jump_to_menu_letter,
    transform_menu_options,
)


def test_transform_menu_options_are_sorted_alphabetically() -> None:
    labels = [label for _, label in transform_menu_options()]
    assert labels == sorted(labels, key=str.casefold)


def test_format_transform_menu_label_highlights_first_letter() -> None:
    assert format_transform_menu_label("Case") == "[bold #268bd2]C[/]ase"


def test_jump_to_menu_letter_selects_first_match() -> None:
    options = transform_menu_options()
    index, last = jump_to_menu_letter(options, "p", current_index=None, last_letter=None)
    labels = [label for _, label in options]
    postpend_index = labels.index("Postpend")
    assert index == postpend_index
    assert last == "p"


def test_jump_to_menu_letter_cycles_shared_prefix() -> None:
    options = transform_menu_options()
    labels = [label for _, label in options]
    prepend_index = labels.index("Prepend")
    postpend_index = labels.index("Postpend")

    first, last = jump_to_menu_letter(
        options,
        "p",
        current_index=None,
        last_letter=None,
    )
    assert first == postpend_index

    second, last = jump_to_menu_letter(
        options,
        "p",
        current_index=first,
        last_letter=last,
    )
    assert second == prepend_index

    third, _last = jump_to_menu_letter(
        options,
        "p",
        current_index=second,
        last_letter=last,
    )
    assert third == postpend_index


def test_add_transform_menu_letter_navigation(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        async with app.run_test() as pilot:
            app.set_focus(None)
            await pilot.pause()
            await pilot.press("a")
            await pilot.pause()

            screen = app.screen
            assert isinstance(screen, AddTransformScreen)
            option_list = screen.query_one("#transform-options")
            labels = [label for _, label in transform_menu_options()]
            postpend_index = labels.index("Postpend")
            prepend_index = labels.index("Prepend")

            await pilot.press("p")
            await pilot.pause()
            assert option_list.highlighted == postpend_index

            await pilot.press("p")
            await pilot.pause()
            assert option_list.highlighted == prepend_index

    asyncio.run(scenario())
