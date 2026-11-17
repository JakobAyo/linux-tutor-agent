# Sources

| Source | What it gives | Status |
|---|---|---|
| zsh `preexec`/`precmd` hook | Command line, time, cwd, exit code, tmux pane | **Primary** ([ADR 0003](../decisions/0003-zsh-hook-observation.md)) |
| `~/.zsh_history` (extended format `: <epoch>:<duration>;<command>`, ~316 KB, ~465 distinct first words) | Past commands, no cwd or exit code | Used once for seeding ([detection/seeding.md](../detection/seeding.md)) |
| `/var/log/pacman.log` | Installed/removed packages, incl. dependencies | TBD (feature idea) |
| Claude Code Bash tool calls (via `../tutor-agent` transcripts) | Commands an agent ran for me | TBD (depends on merge decision) |

Reading `~/.zsh_history` with byte offsets (like tutor-agent's transcript reader) was considered as the primary source: no hook needed, but no exit code or cwd. The hook was chosen instead.

**TBD:** Merge with `../tutor-agent` (one tutor, one shared memory, shell as a second source) or keep a separate tool? For merging: ~80% of its architecture fits, and commands seen in Claude Code sessions would be learned once. Against: tutor-agent has an ADR to observe Claude Code only and is in its M6 daily-use phase; command detection is deterministic and structured, a different pipeline. Brainstorm recommendation: decide after the M0 spike week.
