"""Tests for footer hotkey display."""

from __future__ import annotations

from syren.app import RenameApp


def test_footer_shows_execute_binding() -> None:
    visible_actions = {binding.action for binding in RenameApp.BINDINGS if binding.show}
    assert "execute_rename" in visible_actions
