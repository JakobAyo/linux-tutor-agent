# 0022: Name the command `shtutor`

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
[operations/installation.md](../operations/installation.md) left the command name open (`ltutor`, `shtutor`, `linux-tutor`, …). [architecture/data-storage.md](../architecture/data-storage.md) tied the data directory name to it.

## Decision
The command is `shtutor` (shell tutor). Data lives in `~/.local/share/shtutor/`, settings in `~/.config/shtutor/`.

## Alternatives considered
- `ltutor`: short, but ties the name to Linux rather than the shell.
- `linux-tutor`: matches the repo, but long to type.
- `tutor`: likely to clash with other tools.

## Consequences
- Running `shtutor` with no arguments opens the reader. Other actions become subcommands.
- In M1 the reader still reads the spike's directory (`~/.local/share/linux-tutor-spike/`) until the processor is ported ([ADR 0019](0019-reader-app-first.md)).
- Updated: [operations/installation.md](../operations/installation.md), [architecture/data-storage.md](../architecture/data-storage.md).
