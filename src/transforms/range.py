"""Extract a character range from filenames by index."""

from __future__ import annotations

from dataclasses import dataclass

from .base import FieldSpec, Transform


def apply_range(text: str, start: int, end: int) -> str:
    """Return the inclusive substring from start through end."""
    if start > end:
        return ""
    if not text or start >= len(text):
        return ""
    clamped_start = max(0, start)
    clamped_end = min(end, len(text) - 1)
    if clamped_start > clamped_end:
        return ""
    return text[clamped_start : clamped_end + 1]


def _parse_index(value: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    if not stripped.lstrip("-").isdigit():
        return None
    return int(stripped)


@dataclass
class RangeTransform(Transform):
    start: str = ""
    end: str = ""

    @property
    def name(self) -> str:
        return "range"

    def apply(self, filename: str, file_index: int) -> str:
        del file_index
        start_index = _parse_index(self.start)
        end_index = _parse_index(self.end)
        if start_index is None or end_index is None:
            return filename
        return apply_range(filename, start_index, end_index)

    def field_specs(self) -> tuple[FieldSpec, ...]:
        return (
            FieldSpec("start", "Start index"),
            FieldSpec("end", "End index"),
        )

    def get_field(self, key: str) -> str:
        if key == "start":
            return self.start
        if key == "end":
            return self.end
        raise KeyError(key)

    def set_field(self, key: str, value: str) -> None:
        if key == "start":
            self.start = value
            return
        if key == "end":
            self.end = value
            return
        raise KeyError(key)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> RangeTransform:
        return cls(
            start=fields.get("start", ""),
            end=fields.get("end", ""),
        )
