# 0011: Start the processor automatically, debounced on shell activity

- **Status:** Accepted
- **Date:** 2026-11-17
- **Supersedes:** [0007](0007-manual-processor-in-spike.md)

## Context
Running the processor by hand ([ADR 0007](0007-manual-processor-in-spike.md)) meant I had to remember it, and each run only produced a few cards. I want lessons to appear on their own while I work. Waking up the processor is cheap if it exits at once when there is nothing to do. Only `claude -p` calls cost anything.

## Decision
`precmd` compares `$EPOCHSECONDS` with a timestamp kept in a shell variable (no disk access, no subprocess). If at least 10 minutes have passed since this shell last started the processor, it starts it disowned (`&!`). A lock file ensures that only one processor runs at a time across all shells. The processor exits right away when there are no new log lines and no due backlog items.

## Alternatives considered
- Hourly systemd timer: a session shorter than an hour might never be processed, and it runs while I'm idle.
- Short systemd timer (10–15 min): no work in the shell at all, but it runs when idle, and `claude -p` auth and `notify-send` have to work inside a systemd user unit.
- Start after every command: many pointless wake-ups, and lessons arrive mid-task.
- Also run on shell exit (`zshexit`): catches the end of a short session. Not needed for now, because the next shell's first run picks up the leftover lines.

## Consequences
- Lessons only arrive while I'm actively using the terminal, at most every ~10 minutes per shell.
- Adds a lock file and a background run log, so failures stay visible.
- The hook still never waits: the check is an integer comparison, and the processor is disowned.
- Updated: [operations/background-jobs.md](../operations/background-jobs.md), [milestones/m0-spike.md](../milestones/m0-spike.md).
