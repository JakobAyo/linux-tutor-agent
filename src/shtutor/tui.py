"""The lesson reader: commands on the left, the selected lesson on the right (ADRs 0021, 0024)."""

from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown, OptionList, Static
from textual.widgets.option_list import Option

from shtutor.store import Command, Store, read_lesson

MARKS = {
    "new": ("●", "bold yellow"),
    "seen": ("○", ""),
    "understood": ("✓", "green"),
    "dismissed": ("✗", "dim"),
}
EMPTY = "No lessons yet. They're written in the background while you work in the shell."
POLL_SECONDS = 3


class CommandList(OptionList):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "first", "Top", show=False),
        Binding("G", "last", "Bottom", show=False),
    ]


class LessonPane(VerticalScroll):
    BINDINGS = [
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
        Binding("space", "page_down", "Page down", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
    ]


def row(c: Command) -> Text:
    mark, style = MARKS.get(c.status, ("?", ""))
    text = Text(f"{mark} ", style=style)
    text.append(c.name, style="bold" if c.status == "new" else style)
    text.append(f"  #{c.latest.n}", style="dim")
    return text


class ReaderApp(App[None]):
    TITLE = "shtutor"
    CSS = """
    #list { width: 34; height: 1fr; }
    #right { height: 1fr; }
    #meta { height: 1; padding: 0 1; color: $text-muted; }
    #lesson-pane { padding: 0 1; }
    #filter { display: none; }
    #filter.-visible { display: block; }
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "back", "Back", show=False),
        Binding("u", "toggle('understood')", "Understood"),
        Binding("d", "toggle('dismissed')", "Dismiss"),
        Binding("left_square_bracket", "series(-1)", "Prev lesson", key_display="["),
        Binding("right_square_bracket", "series(1)", "Next lesson", key_display="]"),
        Binding("slash", "filter", "Filter", key_display="/"),
    ]

    def __init__(self, store: Store | None = None) -> None:
        super().__init__()
        self.store = store or Store()
        self.commands: list[Command] = []
        self.shown: list[Command] = []
        self.current: Command | None = None
        self.index = 0  # position of the shown lesson in current.lessons
        self.query_text = ""
        self._version = -1

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="filter by name, Enter to keep, Esc to clear", id="filter")
        with Horizontal():
            yield CommandList(id="list")
            with Vertical(id="right"):
                yield Static(id="meta")
                with LessonPane(id="lesson-pane"):
                    yield Markdown(id="lesson")
        yield Footer()

    def on_mount(self) -> None:
        self.reload()
        self.query_one(CommandList).focus()
        self.set_interval(POLL_SECONDS, self.poll)

    # ------------------------------------------------------------ data

    def poll(self) -> None:
        """Background runs write lessons while the reader is open."""
        if self.store.version() != self._version:
            self.reload()

    def reload(self) -> None:
        self._version = self.store.version()
        self.commands = self.store.commands()
        self.refresh_list()

    def refresh_list(self) -> None:
        keep = self.current.name if self.current else None
        q = self.query_text.lower()
        self.shown = [c for c in self.commands if q in c.name.lower()]
        ol = self.query_one(CommandList)
        ol.clear_options()
        ol.add_options([Option(row(c), id=c.name) for c in self.shown])
        unread = sum(c.status == "new" for c in self.commands)
        self.sub_title = f"{unread} unread · {len(self.commands)} commands"
        if not self.shown:
            self.current = None
            self.query_one("#meta", Static).update("")
            self.query_one(Markdown).update(EMPTY if not q else f"Nothing matches “{self.query_text}”.")
            return
        names = [c.name for c in self.shown]
        ol.highlighted = names.index(keep) if keep in names else 0
        self.show(self.shown[ol.highlighted])

    def show(self, c: Command, index: int | None = None) -> None:
        """Show a lesson of `c`, the latest unless `index` is given. Keeps the scroll position when
        a reload only changed the status of the lesson already on screen."""
        same = self.current is not None and self.current.name == c.name and index is None
        if same and len(self.current.lessons) == len(c.lessons):  # type: ignore[union-attr]
            self.current = c
            self.update_meta()
            return
        self.current = c
        self.index = len(c.lessons) - 1 if index is None else index
        self.query_one(Markdown).update(read_lesson(c.lessons[self.index]))
        self.query_one(LessonPane).scroll_home(animate=False)
        self.update_meta()

    def update_meta(self) -> None:
        c = self.current
        if not c:
            return
        n = c.lessons[self.index].n
        parts = [c.name, f"lesson {n} of {c.latest.n}", c.status, f"used {c.count}×"]
        self.query_one("#meta", Static).update(" · ".join(parts))

    # ------------------------------------------------------------ events

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if event.option_index < len(self.shown):
            self.show(self.shown[event.option_index])

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Enter opens the lesson: focus it, and mark it seen if it's the latest one."""
        c = self.current
        if c and self.index == len(c.lessons) - 1 and self.store.mark_seen(c.name, c.latest.n):
            self.reload()
        self.query_one(LessonPane).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_text = event.value
        self.refresh_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.query_one(CommandList).focus()

    # ------------------------------------------------------------ actions

    def action_back(self) -> None:
        box = self.query_one("#filter", Input)
        if box.has_focus:
            box.value = ""
            box.remove_class("-visible")
        self.query_one(CommandList).focus()

    def action_filter(self) -> None:
        box = self.query_one("#filter", Input)
        box.add_class("-visible")
        box.focus()

    def action_toggle(self, status: str) -> None:
        c = self.current
        if not c:
            return
        new = "seen" if c.status == status else status
        self.store.set_status(c.name, new)
        self.reload()
        hint = {
            "understood": "the next lesson comes in the next background run",
            "dismissed": "no more lessons for it",
        }.get(new, "")
        self.notify(f"{c.name}: {new}" + (f", {hint}" if hint else ""), timeout=3)

    def action_series(self, delta: int) -> None:
        c = self.current
        if c and 0 <= self.index + delta < len(c.lessons):
            self.show(c, self.index + delta)
