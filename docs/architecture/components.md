# Components

One responsibility each. Names are provisional until the package layout is decided.

| Component | Responsibility |
|---|---|
| hook (zsh) | Append one log line per command; nothing else |
| reader | Read new log lines since the last byte offset |
| parser | Split a line into commands, flags, idioms; resolve aliases |
| redactor | Drop secret lines, mask argument values |
| detector | Compare parsed items with the store, emit new items |
| store | Items with status, counts, first seen; atomic writes |
| grounding | Fetch and trim man / `--help` / tldr / pacman info |
| teacher | Build the prompt, call the runner, validate, cache the card |
| runner | Run `claude -p`, timeouts, usage ledger |
| ui | Counter, TUI, zle widgets, CLI |
| installer | Add/remove the hook in `.zshrc`, background units |

**TBD:** Language and package layout. (Leaning: Python 3.12+ with uv, same as `../tutor-agent`, see [tech-stack.md](tech-stack.md).)
