"""Regex substitution in filenames."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .base import FieldSpec, Transform

#: Shown in the preview when the replacement string is not valid.
INVALID_REPLACEMENT = "Invalid"


@dataclass
class SubRegexTransform(Transform):
    pattern: str = ""
    replacement: str = ""
    _compiled: re.Pattern[str] | None = field(default=None, repr=False, compare=False)

    @property
    def name(self) -> str:
        return "sub_regex"

    def _regex(self) -> re.Pattern[str] | None:
        if not self.pattern:
            return None
        if self._compiled is None or self._compiled.pattern != self.pattern:
            try:
                self._compiled = re.compile(self.pattern)
            except re.error:
                self._compiled = None
        return self._compiled

    def apply(self, filename: str, file_index: int) -> str:
        regex = self._regex()
        if regex is None:
            return filename
        try:
            return regex.sub(self.replacement, filename)
        except re.error:
            return INVALID_REPLACEMENT

    def field_specs(self) -> tuple[FieldSpec, ...]:
        return (
            FieldSpec("pattern", "Regex pattern"),
            FieldSpec("replacement", "Replace with"),
        )

    def get_field(self, key: str) -> str:
        if key == "pattern":
            return self.pattern
        if key == "replacement":
            return self.replacement
        raise KeyError(key)

    def set_field(self, key: str, value: str) -> None:
        if key == "pattern":
            self.pattern = value
            self._compiled = None
            return
        if key == "replacement":
            self.replacement = value
            return
        raise KeyError(key)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> SubRegexTransform:
        return cls(
            pattern=fields.get("pattern", ""),
            replacement=fields.get("replacement", ""),
        )
