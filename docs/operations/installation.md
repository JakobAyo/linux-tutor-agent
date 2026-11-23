# Installation

Goal: one command installs the tool and the hook; one command removes both.

- `install`: add a single `source` line to `~/.zshrc` (show the diff, ask, back up), create data directories, set up background units if used.
- `uninstall`: remove the line and units, offer to delete data.
- `seed`: import `~/.zsh_history` ([detection/seeding.md](../detection/seeding.md)).

## Prerequisites
zsh, Claude Code CLI logged in (`claude`), `man`, `tldr`, `pacman`. Optional: tmux, fzf, `notify-send`.

The command is `shtutor` ([ADR 0022](../decisions/0022-command-name-shtutor.md)). With no arguments it opens the reader. During development: `uv tool install --editable .` ([ADR 0020](../decisions/0020-python-with-uv.md)).

**TBD:** Distribution: `uv tool install`, PyPI, AUR package, or several? (See [ci-cd/release.md](../ci-cd/release.md).)
