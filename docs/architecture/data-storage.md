# Data storage

XDG locations:

| Path | Content |
|---|---|
| `~/.local/share/linux-tutor/cmds.log` | Raw command log written by the hook |
| `~/.local/share/linux-tutor/offset` | Byte offset of the last processed log line |
| `~/.local/share/linux-tutor/store.json` | Known items and their status |
| `~/.local/share/linux-tutor/cards/` | Cached cards |
| `~/.local/share/linux-tutor/usage.jsonl` | Usage ledger |
| `~/.config/linux-tutor/settings.toml` | User settings |

Permissions and retention: [security/data-handling.md](../security/data-handling.md).

**TBD:** Store format: one JSON file or SQLite? JSON is simple and diffable; SQLite handles concurrent writers (hook-triggered jobs running in parallel) better.

**TBD:** Final directory name (`linux-tutor`, `shell-tutor`, …) — tied to the project/command name.
