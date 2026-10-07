"""Three-column rename TUI built with Textual and Solarized Dark styling."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, Vertical, VerticalScroll
from textual.events import Click, Key
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import (
    Checkbox,
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
from .rename import execute_rename_plan, validate_rename_plan
from .transforms import (
    create_transform,
    format_transform_menu_label,
    jump_to_menu_letter,
    transform_menu_options,
)
from .transforms.base import FieldSpec, FieldType, Transform

FOOTER_BAR_BACKGROUND = "#073642"
FOOTER_KEY_STYLE = f"bold #b58900 on {FOOTER_BAR_BACKGROUND}"
FOOTER_LABEL_STYLE = "#93a1a1"
FOOTER_HOTKEYS: tuple[tuple[str, str], ...] = (
    ("a", "Add transform"),
    ("f", "Focus filter"),
    ("e", "Execute"),
    ("q", "Quit"),
)
FOOTER_PALETTE_HOTKEY = ("ctrl+p", "Palette")


def format_hotkey_segment(key: str, label: str) -> str:
    """Render one footer hotkey badge and label."""
    key_display = key
    if key.startswith("ctrl+"):
        key_display = f"^{key[5:]}"
    return f"[{FOOTER_KEY_STYLE}] {key_display} [/][{FOOTER_LABEL_STYLE}]{label}[/]"


def footer_primary_hotkey_markup() -> str:
    """Render left-aligned footer hotkeys."""
    return "  ".join(format_hotkey_segment(key, label) for key, label in FOOTER_HOTKEYS)


def footer_palette_hotkey_markup() -> str:
    """Render the right-aligned command palette hotkey."""
    key, label = FOOTER_PALETTE_HOTKEY
    return format_hotkey_segment(key, label)


def footer_hotkey_markup() -> str:
    """Render the bottom-row hotkey help text."""
    return footer_primary_hotkey_markup()


class HotkeyFooter(Horizontal):
    """Always-visible footer row listing app hotkeys."""

    DEFAULT_CSS = """
    HotkeyFooter {
        dock: bottom;
        height: 1;
        width: 1fr;
        background: #073642;
        padding: 0 1;
    }

    HotkeyFooter Static#hotkey-footer-primary {
        width: 1fr;
        height: 1;
        background: transparent;
        content-align: left middle;
    }

    HotkeyFooter Static#hotkey-footer-palette {
        width: auto;
        height: 1;
        background: transparent;
        content-align: right middle;
    }
    """

    def __init__(self) -> None:
        super().__init__(id="hotkey-footer")

    def compose(self) -> ComposeResult:
        yield Static(
            footer_primary_hotkey_markup(),
            id="hotkey-footer-primary",
            markup=True,
        )
        yield Static(
            footer_palette_hotkey_markup(),
            id="hotkey-footer-palette",
            markup=True,
        )


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
        border: none;
        height: auto;
        padding: 0 1 1 1;
        margin-bottom: 0;
        background: #002b36;
    }

    TransformPanel.-selected {
        background: #073642;
    }

    TransformList > TransformPanel:last-child {
        padding-bottom: 0;
    }

    TransformPanel .transform-header {
        height: 1;
        margin-bottom: 0;
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
        background: transparent;
        border: none;
        content-align: center middle;
        text-align: center;
    }

    TransformPanel Static.remove-transform:hover {
        background: #586e75;
        color: #fdf6e3;
    }

    TransformPanel Input {
        background: #073642;
        border: none;
        color: #eee8d5;
        height: 1;
        min-height: 1;
        padding: 0 1;
        margin-bottom: 0;
    }

    TransformPanel.-selected Input {
        background: #002b36;
    }

    TransformPanel Select {
        height: 1;
        background: #586e75;
        border: none;
        color: #eee8d5;
        margin-bottom: 0;
    }

    TransformPanel Select > SelectCurrent {
        height: 1;
        border: none;
        padding: 0 1;
        background: #586e75;
    }

    TransformPanel Select > SelectCurrent Static#label {
        height: 1;
        color: #eee8d5;
        background: transparent;
    }

    TransformPanel Select > SelectCurrent .arrow {
        background: transparent;
        color: #eee8d5;
    }

    TransformPanel .transform-field-row {
        height: 1;
        width: 1fr;
    }

    TransformPanel .transform-field-row Input {
        width: 1fr;
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

    def title_markup(self) -> str:
        """Return the header title, with a red 'Invalid' tag when invalid."""
        if self.transform.is_valid():
            return self.transform.name
        return f"{self.transform.name} [bold #dc322f]Invalid[/]"

    def refresh_title(self) -> None:
        """Update the header title to match the transform validity."""
        title = self.query_one(".transform-name", Static)
        title.update(self.title_markup())

    def compose(self) -> ComposeResult:
        if self.selected:
            self.add_class("-selected")
        with Horizontal(classes="transform-header"):
            yield Static(self.title_markup(), classes="transform-name", markup=True)
            yield Static(" X ", classes="remove-transform", id=f"remove-{self.index}")
        for group, specs in self._field_groups():
            if group is not None:
                with Horizontal(classes="transform-field-row"):
                    for spec in specs:
                        yield from self._compose_field(spec)
            else:
                for spec in specs:
                    yield from self._compose_field(spec)

    def _field_groups(self) -> list[tuple[str | None, tuple[FieldSpec, ...]]]:
        groups: list[tuple[str | None, list[FieldSpec]]] = []
        for spec in self.transform.field_specs():
            if (
                spec.group is not None
                and groups
                and groups[-1][0] == spec.group
            ):
                groups[-1][1].append(spec)
            else:
                groups.append((spec.group, [spec]))
        return [(group, tuple(specs)) for group, specs in groups]

    def _compose_field(self, spec: FieldSpec) -> ComposeResult:
        if spec.field_type is FieldType.SELECT:
            select_options = (
                list(spec.select_options)
                if spec.select_options
                else [(option, option) for option in spec.options]
            )
            yield Select(
                select_options,
                value=self.transform.get_field(spec.key),
                id=f"field-{self.index}-{spec.key}",
                compact=True,
            )
            return
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
        value: object = event.value
        if isinstance(value, tuple):
            value = cast("tuple[object, ...]", value)[0]
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

    def __init__(self) -> None:
        super().__init__()
        self._options = transform_menu_options()
        self._last_letter: str | None = None

    def compose(self) -> ComposeResult:
        yield OptionList(
            *[
                format_transform_menu_label(label)
                for _, label in self._options
            ],
            id="transform-options",
        )

    def on_mount(self) -> None:
        option_list = self.query_one("#transform-options", OptionList)
        if option_list.option_count:
            option_list.highlighted = 0
        self._focus_option_list()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if 0 <= event.option_index < len(self._options):
            self.dismiss(self._options[event.option_index][0])
        else:
            self.dismiss(None)

    def _focus_option_list(self) -> None:
        self.query_one("#transform-options", OptionList).focus()

    def _select_highlighted(self) -> None:
        option_list = self.query_one("#transform-options", OptionList)
        highlighted = option_list.highlighted
        if highlighted is not None and 0 <= highlighted < len(self._options):
            self.dismiss(self._options[highlighted][0])

    def _jump_to_letter(self, letter: str) -> None:
        option_list = self.query_one("#transform-options", OptionList)
        target, self._last_letter = jump_to_menu_letter(
            self._options,
            letter,
            current_index=option_list.highlighted,
            last_letter=self._last_letter,
        )
        if target is None:
            return
        option_list.highlighted = target
        option_list.scroll_to_highlight()
        self._focus_option_list()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            event.stop()
            self.dismiss(None)
            return
        if event.key == "enter":
            event.stop()
            self._select_highlighted()
            return
        if event.character and len(event.character) == 1 and event.character.isalpha():
            event.stop()
            self._jump_to_letter(event.character)


class ConfirmRenameScreen(ModalScreen[bool]):
    """Ask the user to confirm executing a batch rename."""

    BINDINGS = [
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "cancel", "No", show=False),
    ]

    DEFAULT_CSS = """
    ConfirmRenameScreen {
        align: center middle;
    }

    ConfirmRenameScreen Static {
        width: 60;
        max-width: 60;
        border: solid #268bd2;
        background: #073642;
        color: #eee8d5;
        padding: 1 2;
    }
    """

    def __init__(self, count: int) -> None:
        super().__init__()
        self.count = count

    def compose(self) -> ComposeResult:
        yield Static(
            (
                f"Rename {self.count} file(s)? "
                "Press [bold #268bd2]y[/] to confirm or [bold #268bd2]n[/] to cancel."
            ),
            id="confirm-message",
        )

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            event.stop()
            self.dismiss(False)


class ErrorScreen(ModalScreen[None]):
    """Display a rename validation or execution error."""

    DEFAULT_CSS = """
    ErrorScreen {
        align: center middle;
    }

    ErrorScreen Static {
        width: 60;
        max-width: 60;
        border: solid #dc322f;
        background: #073642;
        color: #eee8d5;
        padding: 1 2;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Static(
            f"{self.message}\nPress [bold #268bd2]Esc[/] or [bold #268bd2]Enter[/] to close.",
            id="error-message",
        )

    def on_key(self, event: Key) -> None:
        if event.key in {"escape", "enter"}:
            event.stop()
            self.dismiss(None)


class RenameApp(App[None]):
    """Interactive three-column file rename preview."""

    AUTO_FOCUS = None
    CSS = SOLARIZED_CSS

    BINDINGS = [
        Binding("a", "add_transform", "Add transform"),
        Binding("ctrl+up", "move_transform_up", "Move up", show=False),
        Binding("ctrl+down", "move_transform_down", "Move down", show=False),
        Binding("f", "focus_filter", "Focus filter"),
        Binding("s", "toggle_subdirs", "Subdirs", show=False),
        Binding("h", "toggle_hidden", "Hidden", show=False),
        Binding("i", "toggle_ignore_extension", "Ignore extension", show=False),
        Binding("e", "execute_rename", "Execute"),
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
        self.ignore_extension = False
        self.all_files: list[str] = []
        self.filtered_files: list[str] = []
        self.preview_names: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="main-content"):
            with HorizontalGroup(id="filter-bar"):
                yield Label(format_transform_menu_label("Filter"))
                yield Input(
                    placeholder="glob or fuzzy text",
                    id="file-filter",
                    compact=True,
                )
                yield Checkbox("Include subdirectories", id="include-subdirs")
                yield Checkbox("Include hidden files", id="include-hidden")
                yield Checkbox("Ignore extension", id="ignore-extension")
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
        yield HotkeyFooter()

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

    def focus_transform_field(self, index: int) -> None:
        """Focus the first editable field in a transform panel, if any."""
        container = self.query_one("#transform-list", VerticalScroll)
        for child in container.children:
            if isinstance(child, TransformPanel) and child.index == index:
                for text_input in child.query(Input):
                    text_input.focus()
                    return
                for select in child.query("Select"):
                    select.focus()
                    return
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
            self.call_after_refresh(self._focus_selected_transform)

        self.push_screen(AddTransformScreen(), handle_result)

    def _focus_selected_transform(self) -> None:
        self.focus_transform_field(self.selected_transform)

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

    def action_toggle_ignore_extension(self) -> None:
        checkbox = self.query_one("#ignore-extension", Checkbox)
        checkbox.value = not checkbox.value

    def action_execute_rename(self) -> None:
        pairs = list(zip(self.filtered_files, self.preview_names, strict=True))
        active_pairs = [(source, target) for source, target in pairs if source != target]
        if not active_pairs:
            return

        error = validate_rename_plan(active_pairs, self.directory)
        if error is not None:
            self.push_screen(ErrorScreen(error))
            return

        def handle_confirm(confirmed: bool | None) -> None:
            if not confirmed:
                return
            current_pairs = list(
                zip(self.filtered_files, self.preview_names, strict=True)
            )
            current_active = [
                (source, target)
                for source, target in current_pairs
                if source != target
            ]
            validation_error = validate_rename_plan(current_active, self.directory)
            if validation_error is not None:
                self.push_screen(ErrorScreen(validation_error))
                return
            try:
                execute_rename_plan(current_active, self.directory)
            except ValueError as exc:
                self.push_screen(ErrorScreen(str(exc)))
                return
            self.reload_files()
            self.refresh_preview()
            self.refresh_lists()

        self.push_screen(ConfirmRenameScreen(len(active_pairs)), handle_confirm)

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
        elif event.checkbox.id == "ignore-extension":
            self.ignore_extension = event.value
            self.refresh_preview()
            self.refresh_lists()

    def on_field_changed(self, _event: FieldChanged) -> None:
        self.refresh_preview()
        self.refresh_transform_validity()
        self.refresh_lists()

    def refresh_transform_validity(self) -> None:
        """Mark each transform panel title valid or invalid in place."""
        container = self.query_one("#transform-list", VerticalScroll)
        for child in container.children:
            if isinstance(child, TransformPanel):
                child.refresh_title()

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
        self.preview_names = apply_transforms(
            self.filtered_files,
            self.transforms,
            ignore_extension=self.ignore_extension,
        )

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
