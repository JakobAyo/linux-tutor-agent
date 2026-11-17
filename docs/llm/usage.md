# Usage

`claude -p` on a subscription has rate limits, not per-token billing, but usage still counts.

- Detection makes no LLM calls.
- Lessons are generated eagerly in the background, with no daily cap. Their number follows how much I use the machine ([ADR 0012](../decisions/0012-eager-lessons-without-daily-cap.md)).
- One call per lesson, then cached ([grounding/caching.md](../grounding/caching.md)).
- The history backlog is paced per run, so a fresh seed doesn't fire dozens of calls at once ([detection/seeding.md](../detection/seeding.md)).
- A usage ledger logs each call: time, model, purpose, tokens/cost if `claude -p --output-format json` reports them.
