"""Tests for the transform registry."""

from __future__ import annotations

import pytest

from renfield.transforms import TRANSFORMS, create_transform, register_transform, transform_labels
from renfield.transforms.prepend import PrependTransform


def test_transform_labels_cover_all_registered_transforms() -> None:
    labels = dict(transform_labels())
    assert set(labels) == set(TRANSFORMS)
    assert labels["prepend"] == "Prepend"


def test_create_transform_returns_default_instance() -> None:
    transform = create_transform("prepend")
    assert isinstance(transform, PrependTransform)
    assert transform.text == ""


def test_register_transform_returns_class() -> None:
    class DemoTransform(PrependTransform):
        @property
        def name(self) -> str:
            return "demo-for-test"

    registered = register_transform(DemoTransform)
    assert registered is DemoTransform
    assert "demo-for-test" in TRANSFORMS


def test_create_transform_unknown_name_raises() -> None:
    with pytest.raises(KeyError):
        create_transform("not-a-transform")


def test_transform_clone_creates_independent_copy() -> None:
    transform = PrependTransform(text="abc")
    clone = transform.clone()
    assert isinstance(clone, PrependTransform)
    assert clone.text == "abc"
    clone.set_field("text", "xyz")
    assert transform.text == "abc"
