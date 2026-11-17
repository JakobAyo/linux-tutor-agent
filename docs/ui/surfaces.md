# Surfaces

Push: when lessons are ready, I get a desktop notification. I read them when I want ([ADR 0013](../decisions/0013-notify-when-lessons-are-ready.md)).

| Surface | When | File |
|---|---|---|
| Desktop notification (`notify-send`) | Once per processor run that wrote lessons | [indicators.md](indicators.md) |
| Counter in tmux `status-right` or `RPROMPT` | Optional, always visible | [indicators.md](indicators.md) |
| TUI / dashboard | Browsing and working through waiting lessons, changing status | [tui.md](tui.md) |
| zle widgets (Alt-e, Ctrl-g) | At the prompt, in the moment | [shell-widgets.md](shell-widgets.md) |
| CLI subcommands | Scripting, setup, stats | [operations/installation.md](../operations/installation.md) |

Lessons can pile up ([ADR 0012](../decisions/0012-eager-lessons-without-daily-cap.md)), so the TUI/dashboard is the main place to read them.
