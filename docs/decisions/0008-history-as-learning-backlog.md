# 0008: Seed history as a learning backlog, not as known items

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The plan was to import `~/.zsh_history` and mark its items as familiar, so day one isn't a flood of cards. But many commands in my history were copy-pasted from AI or the web. Using a command often (e.g. `cp`) doesn't mean I know its flags, variations, use cases, or how it combines with other commands. So neither "seen in history" nor "used N times" means "known".

## Decision
Seeding never marks anything as known. Every command, flag, and idiom found in the history becomes a `new` item with its use count. Items are ranked by frequency (most used first), and cards are generated a few at a time, not all at once. Only I set `understood` or `dismissed`.

## Alternatives considered
- All history = known: day one is quiet, but it hides exactly the copy-pasted commands I want to learn.
- Frequency threshold (used N+ times = known): heavy use doesn't mean understanding.
- Ignore history and start empty: every command I run in the first days produces a card, so the flood comes anyway, in random order.

## Consequences
- The flood is avoided by pacing card generation, not by hiding items.
- The most used commands and flags are taught first, which is where knowing them pays off most.
- The backlog can be large (~465 distinct first words, many more flags). Pacing (N per run or day, or on open) is still open ([llm/usage.md](../llm/usage.md)).
- A triage pass is now optional: dismissing items I don't care about, not marking items as known.
- Updated: [detection/seeding.md](../detection/seeding.md), [milestones/m0-spike.md](../milestones/m0-spike.md).
