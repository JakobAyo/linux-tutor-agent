"""Read side of the lesson store, plus status changes.

In M1 the spike still writes the data (ADR 0019), so this reads its directory and follows its
rules: `store.json` is replaced atomically, and every read-modify-write holds `store.lock`.
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STATUSES = ("new", "seen", "understood", "dismissed")


def default_data_dir() -> Path:
    if env := os.environ.get("LTUTOR_SPIKE_DIR"):
        return Path(env)
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local/share")
    return Path(base) / "linux-tutor-spike"


@dataclass(frozen=True)
class Lesson:
    n: int
    path: Path
    time: int
    unverified: tuple[str, ...]


@dataclass(frozen=True)
class Command:
    name: str
    status: str
    count: int
    lessons: tuple[Lesson, ...]

    @property
    def latest(self) -> Lesson:
        return self.lessons[-1]


def _sort_key(c: Command) -> tuple[int, int, str]:
    """Unread first, then by newest lesson."""
    rank = STATUSES.index(c.status) if c.status in STATUSES else len(STATUSES)
    return rank, -c.latest.time, c.name


class Store:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.dir = data_dir or default_data_dir()
        self.file = self.dir / "store.json"
        self.lock_file = self.dir / "store.lock"

    def version(self) -> int:
        """Changes whenever the store file is replaced. 0 if there is none."""
        try:
            return self.file.stat().st_mtime_ns
        except FileNotFoundError:
            return 0

    def _load(self) -> dict[str, Any]:
        try:
            data: dict[str, Any] = json.loads(self.file.read_text())
        except FileNotFoundError:
            return {"commands": {}}
        data.setdefault("commands", {})
        return data

    def commands(self) -> list[Command]:
        """Commands with at least one lesson, unread first."""
        out = []
        for name, item in self._load()["commands"].items():
            lessons = tuple(
                Lesson(
                    n=int(lsn["n"]),
                    path=Path(lsn.get("path") or self.dir / "lessons" / name / f"{lsn['n']}.md"),
                    time=int(lsn.get("time", 0)),
                    unverified=tuple(lsn.get("unverified", ())),
                )
                for lsn in item.get("lessons", [])
            )
            if lessons:
                out.append(Command(name, item.get("status", "new"), int(item.get("count", 0)), lessons))
        return sorted(out, key=_sort_key)

    @contextlib.contextmanager
    def _txn(self) -> Iterator[dict[str, Any]]:
        """Reload, modify, and replace the store under the spike's lock."""
        with self.lock_file.open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = self._load()
            yield data
            tmp = self.file.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=1, sort_keys=True))
            tmp.replace(self.file)

    def set_status(self, name: str, status: str) -> None:
        if status not in STATUSES:
            raise ValueError(f"unknown status: {status}")
        with self._txn() as data:
            if name in data["commands"]:
                data["commands"][name]["status"] = status

    def mark_seen(self, name: str, n: int) -> bool:
        """Opening the latest lesson of a `new` command marks it `seen`. Returns True if it changed."""
        with self._txn() as data:
            item = data["commands"].get(name)
            if item and item.get("status") == "new" and n == len(item.get("lessons", [])):
                item["status"] = "seen"
                return True
        return False


def read_lesson(lesson: Lesson) -> str:
    try:
        return lesson.path.read_text()
    except OSError as e:
        return f"*Can't read lesson {lesson.n}: {e.strerror} ({lesson.path.name})*"
