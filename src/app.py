"""Three-column rename TUI built with Textual and Solarized Dark styling."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, Vertical, VerticalScroll
from textual.events import Click, Key
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import (
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    Select,
    Static,
)

from .colors import SOLARIZED_CSS
from .engine import apply_transforms
from .files import filter_filenames, list_candidate_files
from .transforms import create_transform, transform_labels
from .transforms.base import FieldType, Transform


class FieldChanged(Message):
    """Posted when a transform field value changes."""


class TransformSelected(Message):
    """Posted when the user selects a transform panel."""

    def __init__(self, index: int) -> None:
        self.index = index
        super().__init__()


class TransformRemoved(Message):
    """Posted when the user removes a transform panel."""

    def __init__(self, index: int) -> None:
        self.index = index
        super().__init__()


class TransformPanel(Vertical):
    """Editable panel for one transform in the left column."""

    DEFAULT_CSS = """
    TransformPanel {
        border: solid #586e75;
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        background: #002b36;
    }

    TransformPanel.-selected {
        border: solid #268bd2;
        background: #073642;
    }

    TransformPanel .transform-header {
        height: 1;
        margin-bottom: 1;
    }

    TransformPanel .transform-name {
        color: #b58900;
        text-style: bold;
        height: 1;
        width: 1fr;
        content-align: left middle;
    }

    TransformPanel Static.remove-transform {
        width: 3;
        min-width: 3;
        max-width: 3;
        height: 1;
        color: #dc322f;
        text-style: bold;
        background: #002b36;
        border: none;
        content-align: center middle;
        text-align: center;
    }

    TransformPanel.-selected Static.remove-transform {
        background: #073642;
    }

    TransformPanel Static.remove-transform:hover {
        background: #586e75;
        color: #fdf6e3;
    }

    TransformPanel Input {
        background: #002b36;
        border: none;
        color: #eee8d5;
        height: 1;
        min-height: 1;
        padding: 0 1;
        margin-bottom: 1;
    }

    TransformPanel Select {
        background: #002b36;
        border: none;
        color: #eee8d5;
        margin-bottom: 1;
    }

    TransformPanel Label {
        color: #93a1a1;
        margin-bottom: 0;
    }
    """

    def __init__(self, index: int, transform: Transform, *, selected: bool = False) -> None:
        super().__init__()
        self.index = index
        self.transform = transform
        self.selected = selected

    def set_selected(self, selected: bool) -> None:
        """Highlight this panel when selected for reordering."""
        if selected:
            self.add_class("-selected")
        else:
            self.remove_class("-selected")

    def compose(self) -> ComposeResult:
        if self.selected:
            self.add_class("-selected")
        with Horizontal(classes="transform-header"):
            yield Static(self.transform.name, classes="transform-name")
            yield Static(" X ", classes="remove-transform", id=f"remove-{self.index}")
        for spec in self.transform.field_specs():
            yield Label(spec.label)
            if spec.field_type is FieldType.SELECT:
                yield Select(
                    [(option, option) for option in spec.options],
                    value=self.transform.get_field(spec.key),
                    id=f"field-{self.index}-{spec.key}",
                )
            else:
                yield Input(
                    value=self.transform.get_field(spec.key),
                    placeholder=spec.label,
                    id=f"field-{self.index}-{spec.key}",
                    compact=True,
                )

    def on_input_changed(self, event: Input.Changed) -> None:
        key = self._field_key(event.input.id)
        if key is None:
            return
        self.transform.set_field(key, event.value)
        self.post_message(FieldChanged())

    def on_select_changed(self, event: Select.Changed) -> None:
        key = self._field_key(event.select.id)
        if key is None:
            return
        value = event.value
        if isinstance(value, tuple):
            value = value[0]
        self.transform.set_field(key, str(value))
        self.post_message(FieldChanged())

    def _field_key(self, widget_id: str | None) -> str | None:
        if not widget_id:
            return None
        prefix = f"field-{self.index}-"
        if widget_id.startswith(prefix):
            return widget_id[len(prefix) :]
        return None

    def on_click(self, event: Click) -> None:
        widget = event.widget
        if isinstance(widget, Static) and "remove-transform" in widget.classes:
            self.post_message(TransformRemoved(self.index))
            return
        if isinstance(widget, (Input, Select, Label)):
            return
        self.post_message(TransformSelected(self.index))


class AddTransformScreen(ModalScreen[str | None]):
    """Modal menu for choosing a transform type to add."""

    DEFAULT_CSS = """
    AddTransformScreen {
        align: center middle;
    }

    AddTransformScreen OptionList {
        width: 40;
        height: auto;
        max-height: 14;
        border: solid #268bd2;
        background: #073642;
        padding: 1;
    }

    AddTransformScreen OptionList > .option-list--option-highlight {
        background: #268bd2;
        color: #fdf6e3;
    }
    """

    def compose(self) -> ComposeResult:
        options = [label for _, label in transform_labels()]
        yield OptionList(*options, id="transform-options")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        labels = transform_labels()
        if 0 <= event.option_index < len(labels):
            self.dismiss(labels[event.option_index][0])
        else:
            self.dismiss(None)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            event.stop()
            self.dismiss(None)


class RenameApp(App[None]):
    """Interactive three-column file rename preview."""

    CSS = SOLARIZED_CSS

    BINDINGS = [
        Binding("a", "add_transform", "Add transform"),
        Binding("ctrl+up", "move_transform_up", "Move up", show=False),
        Binding("ctrl+down", "move_transform_down", "Move down", show=False),
        Binding("f", "focus_filter", "Filter", show=False),
        Binding("s", "toggle_subdirs", "Subdirs", show=False),
        Binding("h", "toggle_hidden", "Hidden", show=False),
        Binding("escape", "unfocus", "Unfocus", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, directory: Path | None = None) -> None:
        super().__init__()
        self.directory = (directory or Path.cwd()).resolve()
        self.transforms: list[Transform] = []
        self.selected_transform = 0
        self.filter_text = ""
        self.include_subdirs = False
        self.include_hidden = False
        self.all_files: list[str] = []
        self.filtered_files: list[str] = []
        self.preview_names: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="main-content"):
            with HorizontalGroup(id="filter-bar"):
                yield Label("Filter")
                yield Input(
                    placeholder="glob or fuzzy text",
                    id="file-filter",
                    compact=True,
                )
                yield Checkbox("Include subdirectories", id="include-subdirs")
                yield Checkbox("Include hidden files", id="include-hidden")
            with Horizontal(id="columns"):
                with Vertical(classes="column", id="transform-column"):
                    yield Static("Transforms", classes="column-title")
                    yield VerticalScroll(id="transform-list", classes="TransformList")
                with Vertical(classes="column", id="file-column"):
                    yield Static("Files", classes="column-title")
                    yield ListView(id="file-list", classes="FileList")
                with Vertical(classes="column", id="preview-column"):
                    yield Static("Preview", classes="column-title")
                    yield ListView(id="preview-list", classes="PreviewList")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = str(self.directory)
        self.set_footer_help()
        self.reload_files()
        self.refresh_transform_panels()
        self.refresh_lists()

    def set_footer_help(self) -> None:
        self.title = "syren"

    def action_unfocus(self) -> None:
        if isinstance(self.focused, (Input, Select)):
            self.set_focus(None)

    def action_add_transform(self) -> None:
        def handle_result(name: str | None) -> None:
            if name is None:
                return
            self.transforms.append(create_transform(name))
            self.selected_transform = len(self.transforms) - 1
            self.refresh_transform_panels()
            self.refresh_preview()
            self.refresh_lists()

        self.push_screen(AddTransformScreen(), handle_result)

    def action_move_transform_up(self) -> None:
        if len(self.transforms) < 2:
            return
        index = self.selected_transform
        if index <= 0:
            return
        self.transforms[index - 1], self.transforms[index] = (
            self.transforms[index],
            self.transforms[index - 1],
        )
        self.selected_transform = index - 1
        self.refresh_transform_panels()
        self.refresh_preview()
        self.refresh_lists()

    def action_move_transform_down(self) -> None:
        if len(self.transforms) < 2:
            return
        index = self.selected_transform
        if index >= len(self.transforms) - 1:
            return
        self.transforms[index + 1], self.transforms[index] = (
            self.transforms[index],
            self.transforms[index + 1],
        )
        self.selected_transform = index + 1
        self.refresh_transform_panels()
        self.refresh_preview()
        self.refresh_lists()

    def action_focus_filter(self) -> None:
        self.query_one("#file-filter", Input).focus()

    def action_toggle_subdirs(self) -> None:
        checkbox = self.query_one("#include-subdirs", Checkbox)
        checkbox.value = not checkbox.value

    def action_toggle_hidden(self) -> None:
        checkbox = self.query_one("#include-hidden", Checkbox)
        checkbox.value = not checkbox.value

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "file-filter":
            self.filter_text = event.value
            self.apply_file_filter()
            self.refresh_preview()
            self.refresh_lists()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "include-subdirs":
            self.include_subdirs = event.value
            self.reload_files()
            self.refresh_preview()
            self.refresh_lists()
        elif event.checkbox.id == "include-hidden":
            self.include_hidden = event.value
            self.reload_files()
            self.refresh_preview()
            self.refresh_lists()

    def on_field_changed(self, _event: FieldChanged) -> None:
        self.refresh_preview()
        self.refresh_lists()

    def on_transform_selected(self, event: TransformSelected) -> None:
        if event.index == self.selected_transform:
            return
        self.selected_transform = event.index
        self.update_transform_selection()

    def on_transform_removed(self, event: TransformRemoved) -> None:
        self.remove_transform(event.index)

    def remove_transform(self, index: int) -> None:
        """Remove a transform and refresh the UI."""
        if index < 0 or index >= len(self.transforms):
            return

        del self.transforms[index]

        if not self.transforms:
            self.selected_transform = 0
        elif self.selected_transform > index:
            self.selected_transform -= 1
        elif self.selected_transform == index:
            self.selected_transform = min(index, len(self.transforms) - 1)

        self.refresh_transform_panels()
        self.refresh_preview()
        self.refresh_lists()

    def update_transform_selection(self) -> None:
        """Update panel highlight without rebuilding editable widgets."""
        container = self.query_one("#transform-list", VerticalScroll)
        for child in container.children:
            if isinstance(child, TransformPanel):
                child.set_selected(child.index == self.selected_transform)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "transform-list":
            return
        if event.list_view.id == "file-list":
            preview = self.query_one("#preview-list", ListView)
            index = event.list_view.index or 0
            if index < len(self.preview_names):
                preview.index = index
                preview.scroll_to(index)

    def reload_files(self) -> None:
        self.all_files = list_candidate_files(
            self.directory,
            include_subdirs=self.include_subdirs,
            include_hidden=self.include_hidden,
        )
        self.apply_file_filter()

    def apply_file_filter(self) -> None:
        self.filtered_files = filter_filenames(self.all_files, self.filter_text)

    def refresh_preview(self) -> None:
        if not self.transforms:
            self.preview_names = list(self.filtered_files)
            return
        self.preview_names = apply_transforms(self.filtered_files, self.transforms)

    def refresh_transform_panels(self) -> None:
        container = self.query_one("#transform-list", VerticalScroll)
        container.remove_children()
        if not self.transforms:
            container.mount(
                Static(
                    "Press [bold #268bd2]a[/] to add a transform.",
                    id="transform-empty",
                )
            )
            return

        for index, transform in enumerate(self.transforms):
            container.mount(
                TransformPanel(
                    index,
                    transform,
                    selected=index == self.selected_transform,
                )
            )

    def refresh_lists(self) -> None:
        file_list = self.query_one("#file-list", ListView)
        preview_list = self.query_one("#preview-list", ListView)

        selected = file_list.index or 0
        file_list.clear()
        for name in self.filtered_files:
            file_list.append(ListItem(Label(name)))

        preview_list.clear()
        for name in self.preview_names:
            preview_list.append(ListItem(Label(name)))

        if self.filtered_files:
            file_list.index = min(selected, len(self.filtered_files) - 1)
            preview_list.index = file_list.index


def run(directory: Path | None = None) -> None:
    """Launch the rename TUI."""
    app = RenameApp(directory)
    app.run()
