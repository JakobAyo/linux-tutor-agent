# Shell hooks

Observation uses zsh hooks ([ADR 0003](../decisions/0003-zsh-hook-observation.md)).

## preexec
Gets the full command line before it runs. It only stores the line and the start time (`$EPOCHREALTIME`) in shell variables and writes nothing ([ADR 0005](../decisions/0005-log-line-format.md)).

## precmd
Runs before the next prompt, when `$?` holds the exit code of the last command. It writes one JSON line per command ([ADR 0005](../decisions/0005-log-line-format.md)) with these fields:

| Field | Source |
|---|---|
| time | start time from `preexec` |
| cwd | `$PWD` |
| command | the line stored by `preexec`, JSON-escaped in pure zsh (backslash, quote, newline, tab, control chars) |
| exit code | `$?`, captured as the first statement |
| duration | `$EPOCHREALTIME` now minus the start time |

The exit code lets the tutor treat failed commands differently (typos, "why did that fail?").

Before writing, the hook drops command lines that match the secret skip list ([ADR 0006](../decisions/0006-skip-secrets-in-hook.md), [security/redaction.md](../security/redaction.md)).

The spike must check that other `precmd` hooks (oh-my-zsh, the theme) don't clobber `$?` before ours runs.

## tmux
I'm always inside tmux, so `$TMUX_PANE` can be logged to later capture output with `tmux capture-pane` (for "why did that fail?").

## Triggering background work
The hook never runs detection itself. See [operations/background-jobs.md](../operations/background-jobs.md).
