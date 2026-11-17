# 0010: A series of lessons per command

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The design cached one card per command. A discovery lesson ([ADR 0009](0009-discovery-lessons.md)) can't cover everything about `rsync` or `git` at once, and repeating the same card teaches nothing new. Continuous learning needs a way to go deeper on commands I keep using.

## Decision
Each command gets a series of lessons. Lesson 1 covers my usage, the core flags I'm missing, and the main use cases. Each later lesson knows what earlier lessons taught and goes one level deeper (e.g. `rsync`: 1 core flags and use cases → 2 `--link-dest` snapshots, filters, over ssh → 3 a backup script on a timer). Lessons are cached per command and lesson number.

## Alternatives considered
- One rich card per command, regenerated on request: simpler, but it stops teaching after the first read.

## Consequences
- The store tracks, per command, how many lessons exist and a short summary of what each one taught, so the next one doesn't repeat it.
- The rule for when the next lesson in a series is due is still open ([pedagogy/card-format.md](../pedagogy/card-format.md)).
- Updated: [pedagogy/card-format.md](../pedagogy/card-format.md), [grounding/caching.md](../grounding/caching.md).
