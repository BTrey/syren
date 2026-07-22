"""Base types for modular filename transforms."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Self, cast


class FieldType(str, Enum):
    TEXT = "text"
    SELECT = "select"


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    field_type: FieldType = FieldType.TEXT
    options: tuple[str, ...] = ()


NUMBER_PATTERN = re.compile(r"#(\d+)")


def expand_numbered(text: str, file_index: int) -> str:
    """Replace the first #NNN token with an incrementing zero-padded number."""

    def replacer(match: re.Match[str]) -> str:
        num_str = match.group(1)
        value = int(num_str) + file_index
        return str(value).zfill(len(num_str))

    return NUMBER_PATTERN.sub(replacer, text, count=1)


def split_stem(filename: str) -> tuple[str, str]:
    """Split a filename into stem and suffix (including the dot)."""
    if filename.startswith(".") and filename.count(".") == 1:
        return filename, ""
    dot = filename.rfind(".")
    if dot <= 0:
        return filename, ""
    return filename[:dot], filename[dot:]


class Transform(ABC):
    """A single filename transform with configurable fields."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier used in the transform registry."""

    @abstractmethod
    def apply(self, filename: str, file_index: int) -> str:
        """Return filename after applying this transform."""

    @abstractmethod
    def field_specs(self) -> tuple[FieldSpec, ...]:
        """Describe editable fields for the TUI."""

    @abstractmethod
    def get_field(self, key: str) -> str:
        """Return the string value for a field key."""

    @abstractmethod
    def set_field(self, key: str, value: str) -> None:
        """Update a field value from the TUI."""

    def clone(self) -> Self:
        """Return a deep copy suitable for editing."""
        cls = type(self)
        return cast(
            Self,
            cls.from_fields(
                {spec.key: self.get_field(spec.key) for spec in self.field_specs()}
            ),
        )

    @classmethod
    @abstractmethod
    def from_fields(cls, fields: dict[str, str]) -> Transform:
        """Construct a transform from field values."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.name,
            "fields": {spec.key: self.get_field(spec.key) for spec in self.field_specs()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transform:
        raise NotImplementedError
