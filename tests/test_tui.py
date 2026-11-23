from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

from textual.pilot import Pilot
from textual.widgets import Static

from shtutor.store import Store
from shtutor.tui import LessonPane, ReaderApp


def run(store: Store, steps: Callable[[ReaderApp, Pilot[None]], Awaitable[None]]) -> None:
    async def main() -> None:
        app = ReaderApp(store)
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.pause()
            await steps(app, pilot)

    asyncio.run(main())


def status(store: Store, cmd: str) -> str:
    return json.loads(store.file.read_text())["commands"][cmd]["status"]


def meta(app: ReaderApp) -> str:
    return str(app.query_one("#meta", Static).render())


def test_opens_on_the_first_unread_command(store: Store) -> None:
    async def steps(app: ReaderApp, pilot: Pilot[None]) -> None:
        assert app.current is not None and app.current.name == "find"
        assert app.sub_title == "2 unread · 3 commands"

    run(store, steps)


def test_moving_previews_and_enter_marks_seen(store: Store) -> None:
    async def steps(app: ReaderApp, pilot: Pilot[None]) -> None:
        await pilot.press("j")
        assert app.current is not None and app.current.name == "rsync"
        assert status(store, "rsync") == "new"  # a preview isn't a read
        await pilot.press("enter")
        assert status(store, "rsync") == "seen"
        assert isinstance(app.focused, LessonPane)
        await pilot.press("escape")
        assert not isinstance(app.focused, LessonPane)

    run(store, steps)


def test_understood_and_dismissed_toggle(store: Store) -> None:
    async def steps(app: ReaderApp, pilot: Pilot[None]) -> None:
        await pilot.press("u")
        assert status(store, "find") == "understood"
        await pilot.press("u")
        assert status(store, "find") == "seen"
        await pilot.press("d")
        assert status(store, "find") == "dismissed"

    run(store, steps)


def test_brackets_walk_the_series(store: Store) -> None:
    async def steps(app: ReaderApp, pilot: Pilot[None]) -> None:
        await pilot.press("/", "g", "i", "t", "enter")
        assert app.current is not None and app.current.name == "git"
        assert "lesson 2 of 2" in meta(app)
        await pilot.press("[")
        assert "lesson 1 of 2" in meta(app)
        await pilot.press("[")  # already at the first lesson
        assert "lesson 1 of 2" in meta(app)
        await pilot.press("]")
        assert "lesson 2 of 2" in meta(app)

    run(store, steps)


def test_filter_escape_clears_it(store: Store) -> None:
    async def steps(app: ReaderApp, pilot: Pilot[None]) -> None:
        await pilot.press("/", "r", "s")
        assert [c.name for c in app.shown] == ["rsync"]
        await pilot.press("escape")
        assert len(app.shown) == 3

    run(store, steps)


def test_picks_up_lessons_from_a_background_run(store: Store) -> None:
    async def steps(app: ReaderApp, pilot: Pilot[None]) -> None:
        data = json.loads(store.file.read_text())
        data["commands"]["tar"]["lessons"] = [
            {"n": 1, "path": str(store.dir / "tar.md"), "time": 999, "unverified": []}
        ]
        store.file.write_text(json.dumps(data))
        app.poll()
        await pilot.pause()
        assert [c.name for c in app.shown][0] == "tar"  # newest unread first

    run(store, steps)
