# 0015: Three backlog lessons per background run

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
There is no daily cap ([ADR 0012](0012-eager-lessons-without-daily-cap.md)), but writing lessons for the whole seeded history in one run would fire dozens of `claude -p` calls at once and could hit subscription rate limits. Runs happen at most every 10 minutes per shell while I'm active ([ADR 0011](0011-activity-debounced-trigger.md)).

## Decision
Each background run writes lessons for all new commands and all due series lessons, plus up to 3 lessons from the history backlog, most used first.

## Alternatives considered
- 1 per run: the backlog would take a week or two to clear.
- 5 per run: it clears faster, but heavy sessions risk rate limits.

## Consequences
- Up to ~18 backlog lessons an hour of active use. A backlog of ~90 clears within a few days of normal use.
- Updated: [detection/seeding.md](../detection/seeding.md).
