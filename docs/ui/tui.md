# TUI

A terminal UI built with Textual ([ADR 0021](../decisions/0021-textual-tui-reader.md)), opened by running `shtutor` from any directory ([ADR 0022](../decisions/0022-command-name-shtutor.md)). It's for browsing and working through lessons: a list of items by status, a lesson view, keys to change status (`understood`, `dismissed`), and regenerating a lesson. Lessons pile up by design ([ADR 0012](../decisions/0012-eager-lessons-without-daily-cap.md)), so this is the main place to read them. Clicking a notification opens it ([ADR 0016](../decisions/0016-notifications-only-no-counter.md)). It is built first, in M1 ([ADR 0019](../decisions/0019-reader-app-first.md)).

## Layout and keys
Two panes: commands with lessons on the left (unread first), the selected lesson on the right ([ADR 0024](../decisions/0024-reader-layout-and-keys.md)).

| Key | Action |
|---|---|
| `j` / `k` | Move in the list, or scroll the lesson |
| `Enter` | Open the lesson (focus it, mark it `seen`) |
| `Esc` | Back to the list |
| `u` / `d` | Mark `understood` / `dismissed` (press again to undo) |
| `[` / `]` | Previous / next lesson in the series |
| `/` | Filter the list by name |
| `q` | Quit |

## Opening it
- From any directory: `shtutor`.
- From a notification: a click opens it in a new kitty window with the class `shtutor` ([ADR 0023](../decisions/0023-notification-click-opens-kitty.md)).
