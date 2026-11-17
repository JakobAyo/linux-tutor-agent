# 0016: Notifications only, no unread counter, no click action yet

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
[ADR 0013](0013-notify-when-lessons-are-ready.md) left open whether a tmux/RPROMPT unread counter is also wanted, and what clicking a notification should do. Lessons will later be read in a dedicated TUI or web UI, not in tmux windows.

## Decision
- No unread counter in tmux `status-right` or `RPROMPT`.
- The notification only informs me. It has no click action until the TUI/web UI exists. Then a click opens it.

## Alternatives considered
- tmux counter as well: more always-visible noise. The future UI will show what's waiting.
- Click opens a new tmux window: ties the UX to tmux, while lessons will live in their own UI.

## Consequences
- During the spike I read lessons with `process.py read`.
- Updated: [ui/indicators.md](../ui/indicators.md), [ui/surfaces.md](../ui/surfaces.md), [ui/tui.md](../ui/tui.md).
