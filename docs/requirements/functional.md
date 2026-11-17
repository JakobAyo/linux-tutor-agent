# Functional requirements

## Core (the learning loop)
- **F1 Observe:** record every interactive zsh command line with time, working directory, and exit code. See [observation/](../observation/).
- **F2 Detect:** find what is new to me at three levels: new command, new flag on a known command, new shell idiom. See [detection/](../detection/).
- **F3 Teach:** write a card for each new item, grounded in local docs and based on the exact command I ran. See [pedagogy/card-format.md](../pedagogy/card-format.md).
- **F4 Track:** each item has a status `new` → `seen` → `understood` (set by me) or `dismissed`. See [pedagogy/learner-model.md](../pedagogy/learner-model.md).
- **F5 Seed:** bootstrap the known store from `~/.zsh_history` so day one isn't a flood. See [detection/seeding.md](../detection/seeding.md).

## Feature ideas (roughly by value per effort)

| Idea | What it does | Effort | Status |
|---|---|---|---|
| Explain before running | A zle widget (e.g. Alt-e) explains the current `$BUFFER` before Enter. Good for commands copied from the Arch Wiki and for catching dangerous ones (`dd`, `rm -rf`) | Small | TBD |
| Cards for new commands | The core loop, lessons cached per command | Medium | Core |
| "Why did that fail?" | After a non-zero exit, `tmux capture-pane -p -S -40` grabs the output and the tutor explains the error | Small | TBD |
| Personal cheat sheet + fzf | A key (e.g. Ctrl-g) fuzzy-searches learned variations and inserts the chosen one into the prompt | Small | TBD |
| Concept lessons | Group commands into mechanisms (systemd, journald, pacman/AUR, permissions, signals, fds) | Medium | TBD |
| pacman.log watcher | Watch `/var/log/pacman.log`: what a newly installed package is and why it's there | Small | TBD |
| Daily recall | Three questions a day ("how do you show errors from the last boot?") | Medium | TBD |

**TBD:** Which feature ideas are in scope, and in which milestone? (Brainstorm order is by value per effort, top first.)

## Existing tools (don't reinvent)
- `tldr` (installed): community example pages, good grounding data.
- `man`, `apropos` / `man -k`, `whatis`: local docs and search.
- explainshell.com: flag-by-flag explanation of a command line.
- `navi`: interactive cheat sheets with fzf.
- `atuin`: shell history in SQLite with exit code, cwd, and duration.
- `cht.sh` (`curl cht.sh/tar`): cheat sheets over HTTP.

The tutor reuses `man`, `--help`, `tldr`, and `pacman` as grounding. Not installed: `atuin`, `navi`, `tealdeer`.
