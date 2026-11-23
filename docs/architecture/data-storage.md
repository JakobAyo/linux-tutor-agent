# Data storage

XDG locations:

| Path | Content |
|---|---|
| `~/.local/share/shtutor/cmds.log` | Raw command log written by the hook |
| `~/.local/share/shtutor/offset` | Byte offset of the last processed log line |
| `~/.local/share/shtutor/store.json` | Known items and their status |
| `~/.local/share/shtutor/cards/` | Cached cards |
| `~/.local/share/shtutor/usage.jsonl` | Usage ledger |
| `~/.config/shtutor/settings.toml` | User settings |

Permissions and retention: [security/data-handling.md](../security/data-handling.md).

**TBD:** Store format: one JSON file or SQLite? JSON is simple and diffable; SQLite handles concurrent writers (hook-triggered jobs running in parallel) better.

The directory name follows the command name ([ADR 0022](../decisions/0022-command-name-shtutor.md)). In M1 the reader reads the spike's `~/.local/share/linux-tutor-spike/` until the processor is ported ([ADR 0019](../decisions/0019-reader-app-first.md)).
