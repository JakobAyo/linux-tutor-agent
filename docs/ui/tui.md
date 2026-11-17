# TUI / web UI

A dedicated UI to browse and work through lessons: a list of items by status, a lesson view, keys to change status (`understood`, `dismissed`), regenerate a lesson. Lessons pile up by design ([ADR 0012](../decisions/0012-eager-lessons-without-daily-cap.md)), so this is the main place to read them. Clicking a notification will open it ([ADR 0016](../decisions/0016-notifications-only-no-counter.md)). Until it exists, the spike uses Markdown files and an fzf picker.

**TBD:** A terminal UI (TUI) or a local web UI?

**TBD:** Framework (e.g. Textual for a TUI)? Key bindings?
