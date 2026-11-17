# Usage

`claude -p` on a subscription has rate limits, not per-token billing, but usage still counts.

- Detection makes no LLM calls.
- One call per new card, then cached ([grounding/caching.md](../grounding/caching.md)).
- A usage ledger logs each call: time, model, purpose, tokens/cost if `claude -p --output-format json` reports them.

**TBD:** Generate cards eagerly in the background when an item is detected, or lazily when I open it? (Lazy saves calls for items I never open; eager makes cards instant.)

**TBD:** Daily cap on calls?
