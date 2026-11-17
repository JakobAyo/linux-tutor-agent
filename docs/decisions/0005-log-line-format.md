# 0005: One JSON line per command, written in precmd

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The hook has to record the command line, time, working directory, and exit code ([ADR 0003](0003-zsh-hook-observation.md)). The command line is known in `preexec`, but the exit code only in `precmd`. Command lines can contain tabs, quotes, and newlines.

## Decision
`preexec` only stores the command line and start time in shell variables. `precmd` writes one complete JSON line (JSONL) per command with these fields: time, cwd, command, exit code, and duration (from the `$EPOCHREALTIME` difference).

## Alternatives considered
- Two lines (`preexec` + `precmd`) joined later: a command is still logged if the shell dies while it runs, but the reader has to pair lines, which breaks with multiple shells writing to the same log.
- Tab-separated text: a bit cheaper to write, but escaping tabs and newlines by hand is error-prone, and adding a field later breaks old lines.

## Consequences
- Each line is self-contained, so the processor can read it with `json.loads` and no joining step.
- The hook must JSON-escape the command (backslash, quote, newline, tab, other control characters) in pure zsh, without starting a subprocess.
- A command that never returns to a prompt (the shell is killed, or `exec`) is not logged. That's acceptable.
- Duration is recorded, so slow or long-running commands can be told apart later.
- Updated: [observation/shell-hooks.md](../observation/shell-hooks.md).
