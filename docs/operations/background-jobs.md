# Background jobs

The hook never blocks the shell. Detection and card writing run in the background.

| Option | How | Trade-off |
|---|---|---|
| `&!` from the hook | `precmd` starts `linux-tutor process &!` (disowned) | Simple; spawns a process per command, needs a lock against parallel runs |
| systemd user `.path` unit | Watches `cmds.log`, starts a `.service` on change | No work in the shell at all; more setup, systemd-specific |
| Periodic timer | systemd timer every N minutes | Simplest, but delayed |

**M0 spike:** no automatic trigger. I run the processor by hand ([ADR 0007](../decisions/0007-manual-processor-in-spike.md)).

**TBD:** Which trigger for the real tool, after the spike? (Brainstorm options: `&!` or a systemd `.path` unit.)

**TBD:** Concurrency: a lock file so only one processor runs at a time? Not needed while it runs by hand.
