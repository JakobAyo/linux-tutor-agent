# Shell hooks

Observation uses zsh hooks ([ADR 0003](../decisions/0003-zsh-hook-observation.md)).

## preexec
Gets the full command line before it runs. Appending one line takes microseconds:

```zsh
zmodload zsh/datetime; autoload -Uz add-zsh-hook
_learn() { print -r -- "$EPOCHSECONDS	$PWD	$1" >> ~/.local/share/linux-tutor/cmds.log }
add-zsh-hook preexec _learn
```

## precmd
Runs before the next prompt; `$?` holds the exit code of the last command. Recording it lets the tutor treat failed commands differently (typos, "why did that fail?").

**TBD:** Log line format: one line written in `preexec` and a second in `precmd` (joined later), or buffer in `preexec` and write one complete line in `precmd`? Also: tab-separated text or JSON lines, and how to escape multi-line commands?

**TBD:** Record command duration too (`$EPOCHREALTIME` difference)?

## tmux
I'm always inside tmux, so `$TMUX_PANE` can be logged to later capture output with `tmux capture-pane` (for "why did that fail?").

## Triggering background work
The hook never runs detection itself. See [operations/background-jobs.md](../operations/background-jobs.md).
