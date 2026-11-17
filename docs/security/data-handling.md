# Data handling

- All data stays local under XDG paths (`~/.local/share/linux-tutor/`, `~/.config/linux-tutor/`). See [architecture/data-storage.md](../architecture/data-storage.md).
- Files are created with mode `0600`, directories `0700`.
- Nothing is uploaded except the redacted prompt to `claude -p`.
- Uninstall offers to delete all data.

**TBD:** Retention: keep the raw command log forever, rotate it (e.g. 30 days), or delete lines once they're processed?
