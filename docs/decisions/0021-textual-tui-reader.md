# 0021: A Textual TUI for reading lessons

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
[ui/tui.md](../ui/tui.md) left open whether lessons are read in a terminal UI or a local web UI, and which framework to use.

## Decision
A terminal UI built with Textual. It runs in any terminal, inside tmux, or as a tmux popup.

## Alternatives considered
- Local web UI: easier to open from a notification and nicer typography, but it takes me out of the terminal, which is what the tool is meant to teach, and it needs a server running in the background.
- fzf plus a Markdown pager: cheapest, but no room for status keys, navigating a series, or stats.

## Consequences
- Lessons stay Markdown. Textual renders them.
- A notification click has to start a terminal that runs the TUI.
- Key bindings are still open.
- Updated: [ui/tui.md](../ui/tui.md), [architecture/tech-stack.md](../architecture/tech-stack.md).
