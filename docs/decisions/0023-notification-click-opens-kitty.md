# 0023: A notification click opens the reader in a new kitty window

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
[ADR 0016](0016-notifications-only-no-counter.md) said a click opens the reader once it exists. In the M0 week a click did nothing, and that's the main reason I didn't read the lessons ([ADR 0019](0019-reader-app-first.md)). [ui/tui.md](../ui/tui.md) left open where the reader opens: a new terminal window, or a window in the running tmux session.

## Decision
The notification gets a default action. Clicking it opens `shtutor` in a new kitty window (`kitty --class shtutor shtutor`). A detached child process waits for the click, so the background run doesn't block on it. If `shtutor` or `kitty` isn't on `PATH`, the notification has no action, as before.

## Alternatives considered
- A new window in the running tmux session: stays in my workflow, but I don't see it unless the terminal is focused and on that session. With several sessions, which one is ambiguous.

## Consequences
- It works even when no terminal is in front of me. I close the window when I'm done.
- The window class `shtutor` lets Hyprland rules float or size it.
- kitty is hard-coded for now. A setting for the terminal comes with the settings file.
- Updated: [ui/tui.md](../ui/tui.md), [ui/indicators.md](../ui/indicators.md).
