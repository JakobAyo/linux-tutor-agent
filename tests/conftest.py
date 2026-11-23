from __future__ import annotations

import json
from pathlib import Path

import pytest

from shtutor.store import Store


def lesson(data: Path, cmd: str, n: int, time: int) -> dict[str, object]:
    path = data / "lessons" / cmd / f"{n}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {cmd} — lesson {n}\n\nBody of {cmd} lesson {n}.\n")
    return {"n": n, "path": str(path), "time": time, "taught": "", "next": "", "unverified": [], "count_at": 1}


@pytest.fixture
def store(tmp_path: Path) -> Store:
    """A spike-shaped store: two unread commands, one seen with a series, one without lessons."""
    data = tmp_path / "data"
    commands = {
        "rsync": {"status": "new", "count": 5, "lessons": [lesson(data, "rsync", 1, 100)]},
        "find": {"status": "new", "count": 9, "lessons": [lesson(data, "find", 1, 200)]},
        "git": {
            "status": "seen",
            "count": 40,
            "lessons": [lesson(data, "git", 1, 50), lesson(data, "git", 2, 300)],
        },
        "tar": {"status": "new", "count": 3, "lessons": []},
    }
    for item in commands.values():
        item.update({"source": "history", "piped": 0, "flags": {}, "shapes": {}})
    (data / "store.json").write_text(json.dumps({"commands": commands}))
    return Store(data)
