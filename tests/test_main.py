"""Tests for package entry points."""

from __future__ import annotations

from unittest.mock import patch

from syren.__main__ import main


def test_main_launches_app_and_returns_zero() -> None:
    with patch("syren.__main__.RenameApp") as mock_app:
        assert main() == 0
        mock_app.return_value.run.assert_called_once()
