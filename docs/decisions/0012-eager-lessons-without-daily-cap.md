# 0012: Generate lessons eagerly, without a daily cap

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
With an automatic trigger ([ADR 0011](0011-activity-debounced-trigger.md)), something has to decide how many lessons to write. The options were lazy generation (only when I open an item), a daily cap, or no cap. Later there will be a dashboard or TUI where I work through waiting lessons at my own pace.

## Decision
Lessons are generated eagerly in the background as items are detected. There is no daily cap: the number of lessons follows how much I use the machine. A pile of unread lessons is fine, because the dashboard/TUI is where I work through them.

## Alternatives considered
- Lazy generation on open: saves calls, but lessons aren't ready when I want to read them, and nothing new can be announced.
- A daily cap (1, 3, or 5): keeps it from feeling like homework, but it throttles learning on busy days for no real benefit.

## Consequences
- Subscription rate limits still apply. The backlog is paced per run (see [detection/seeding.md](../detection/seeding.md)), and the usage ledger shows how much is spent.
- A dashboard/TUI for browsing lessons becomes more important ([ui/surfaces.md](../ui/surfaces.md)).
- Updated: [llm/usage.md](../llm/usage.md).
