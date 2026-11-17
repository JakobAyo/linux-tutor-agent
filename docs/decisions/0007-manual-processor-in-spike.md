# 0007: Run the processor by hand during the M0 spike

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The hook only appends to a log. A separate processor reads the log, detects new items, and calls `claude -p`, which takes seconds per card. Something has to start it: me, a background process after each command (`&!`), a systemd `.path` unit, or a timer ([operations/background-jobs.md](../operations/background-jobs.md)).

## Decision
For the M0 spike, I start the processor by hand (e.g. `spike/process`). There is no automatic trigger.

## Alternatives considered
- `&!` after each command: cards appear almost immediately, but it needs a lock against parallel runs, and `claude -p` auth has to work in a detached process.
- systemd `.path` unit or timer: no work in the shell, but it needs `claude -p` auth to work in a systemd user unit ([llm/runner.md](../llm/runner.md)).

## Consequences
- The spike needs no lock file and no background auth.
- It doubles as a test of pull-style use: whether I come back and run it on my own ([ui/surfaces.md](../ui/surfaces.md)).
- The trigger for the real tool stays open until after the spike.
- Updated: [operations/background-jobs.md](../operations/background-jobs.md), [milestones/m0-spike.md](../milestones/m0-spike.md).
