# Sources

| Source | What it gives | Status |
|---|---|---|
| zsh `preexec`/`precmd` hook | Command line, time, cwd, exit code, tmux pane | **Primary** ([ADR 0003](../decisions/0003-zsh-hook-observation.md)) |
| `~/.zsh_history` (extended format `: <epoch>:<duration>;<command>`, ~316 KB, ~465 distinct first words) | Past commands, no cwd or exit code | Used once for seeding ([detection/seeding.md](../detection/seeding.md)) |
| `/var/log/pacman.log` | Installed/removed packages, incl. dependencies | TBD (feature idea) |

Reading `~/.zsh_history` with byte offsets was considered as the primary source: no hook needed, but no exit code or cwd. The hook was chosen instead.
