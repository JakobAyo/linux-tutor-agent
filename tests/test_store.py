from __future__ import annotations

import json

import pytest

from shtutor.store import Store, read_lesson


def raw(store: Store) -> dict:
    return json.loads(store.file.read_text())["commands"]


def test_lists_only_commands_with_lessons_unread_first(store: Store) -> None:
    assert [c.name for c in store.commands()] == ["find", "rsync", "git"]


def test_latest_lesson_is_last_in_series(store: Store) -> None:
    git = next(c for c in store.commands() if c.name == "git")
    assert git.latest.n == 2
    assert "git lesson 2" in read_lesson(git.latest)


def test_set_status_keeps_the_rest_of_the_item(store: Store) -> None:
    store.set_status("git", "understood")
    item = raw(store)["git"]
    assert item["status"] == "understood"
    assert item["count"] == 40 and len(item["lessons"]) == 2


def test_set_status_rejects_unknown_status(store: Store) -> None:
    with pytest.raises(ValueError):
        store.set_status("git", "done")


def test_mark_seen_only_for_the_latest_lesson_of_a_new_command(store: Store) -> None:
    assert store.mark_seen("rsync", 1)
    assert raw(store)["rsync"]["status"] == "seen"
    assert not store.mark_seen("rsync", 1)  # already seen
    store.set_status("git", "new")
    assert not store.mark_seen("git", 1)  # an older lesson doesn't count
    assert raw(store)["git"]["status"] == "new"


def test_missing_store_is_empty(tmp_path) -> None:
    s = Store(tmp_path / "nothing")
    assert s.commands() == [] and s.version() == 0


def test_unreadable_lesson_is_reported_not_raised(store: Store) -> None:
    rsync = next(c for c in store.commands() if c.name == "rsync")
    rsync.latest.path.unlink()
    assert "Can't read lesson 1" in read_lesson(rsync.latest)
