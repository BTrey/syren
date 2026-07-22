"""Literal substring replacement in filenames."""

from __future__ import annotations

from dataclasses import dataclass

from .base import FieldSpec, Transform


@dataclass
class ReplaceTransform(Transform):
    find: str = ""
    replace: str = ""

    @property
    def name(self) -> str:
        return "replace"

    def apply(self, filename: str, file_index: int) -> str:
        if not self.find:
            return filename
        return filename.replace(self.find, self.replace)

    def field_specs(self) -> tuple[FieldSpec, ...]:
        return (
            FieldSpec("find", "Find"),
            FieldSpec("replace", "Replace with"),
        )

    def get_field(self, key: str) -> str:
        if key == "find":
            return self.find
        if key == "replace":
            return self.replace
        raise KeyError(key)

    def set_field(self, key: str, value: str) -> None:
        if key == "find":
            self.find = value
            return
        if key == "replace":
            self.replace = value
            return
        raise KeyError(key)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> ReplaceTransform:
        return cls(find=fields.get("find", ""), replace=fields.get("replace", ""))
