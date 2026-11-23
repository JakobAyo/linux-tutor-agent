# 0024: Reader layout and vim-style keys

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
[ui/tui.md](../ui/tui.md) left the reader's layout and key bindings open. I use vim-style keys in tmux (`h`/`j`/`k`/`l` for panes).

## Decision
Two panes: the list of commands with lessons on the left (unread first), and the selected lesson on the right.

| Key | Action |
|---|---|
| `j` / `k` | Move in the list, or scroll the lesson |
| `Enter` | Open the lesson (focus it, mark it `seen`) |
| `Esc` | Back to the list |
| `u` | Mark `understood` (press again to undo) |
| `d` | Mark `dismissed` (press again to undo) |
| `[` / `]` | Previous / next lesson in the series |
| `/` | Filter the list by name |
| `q` | Quit |

## Alternatives considered
- One pane at a time (list, then full-screen lesson): more room for the lesson, but no preview while moving through the list.

## Consequences
- Moving through the list only previews. A lesson counts as `seen` when I open it with `Enter`.
- Updated: [ui/tui.md](../ui/tui.md).
