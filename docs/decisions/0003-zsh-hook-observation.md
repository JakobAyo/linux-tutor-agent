# 0003: Observe commands with a zsh hook

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The tutor must see the commands I run. I use zsh with oh-my-zsh, always inside tmux.

## Decision
A zsh `preexec` hook (plus `precmd` for the exit code) appends each command line to a log. The hook does nothing else; all processing runs in the background.

## Alternatives considered
- Read `~/.zsh_history` with byte offsets: no hook needed, but no exit code or working directory, and depends on history settings. Kept for one-time seeding.
- `atuin`: has exit code, cwd, and duration in SQLite, but isn't installed and adds a dependency.

## Consequences
- Exit code and cwd are available (typo filtering, "why did that fail?").
- Only zsh is supported at first ([vision/non-goals.md](../vision/non-goals.md) has the TBD on other shells).
- The hook must stay trivially fast and must never print or fail visibly ([requirements/non-functional.md](../requirements/non-functional.md)).
