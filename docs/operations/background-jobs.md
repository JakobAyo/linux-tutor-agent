# Background jobs

The hook never blocks the shell. Detection and card writing run in the background.

| Option | How | Trade-off |
|---|---|---|
| `&!` from the hook | `precmd` starts `linux-tutor process &!` (disowned) | Simple; spawns a process per command, needs a lock against parallel runs |
| systemd user `.path` unit | Watches `cmds.log`, starts a `.service` on change | No work in the shell at all; more setup, systemd-specific |
| Periodic timer | systemd timer every N minutes | Simplest, but delayed |

**TBD:** Which trigger? (Brainstorm options: `&!` or a systemd `.path` unit.)

**TBD:** Concurrency: a lock file so only one processor runs at a time (like tutor-agent's ADR 0032)?
