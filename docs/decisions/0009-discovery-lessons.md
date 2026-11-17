# 0009: Lessons teach discovery, anchored to my commands

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The first spike cards read like a personal `tldr`: what the command does and the flags I used. That only explains what I already type. The real goal is continuous learning: get new ideas, stay motivated, and over time become a confident terminal user who writes their own scripts and automations. The docs said "not a general Linux course, no curriculum detached from what I use", which left open how far a lesson may go beyond my exact command.

## Decision
A lesson starts from a command I ran, then teaches what I probably don't know yet:
- flags and modes I haven't used, with concrete use cases,
- combinations with other commands (pipes, `xargs`, `find -exec`, scripts, systemd units),
- related or better tools in the same area (e.g. `grep` → `rg`, `find` → `fd`, `rsync` → a backup script on a systemd timer),
- the concept behind it, where it helps.

Nothing unrelated to my commands. The neighbours are reached from something I used.

## Alternatives considered
- Anchored only (unused flags and combos with commands I already use, no new tools): safer, but it can't lead me to tools I don't know exist.
- Anchored plus a separate curriculum track (e.g. "shell scripting", "networking"): more complete, but it's a course detached from my work, and much more to build. Can be revisited later.

## Consequences
- Answers the "main goal" question: discovery and continuous learning across commands, flags, combinations, and concepts.
- Lessons are longer and more opinionated than a reference card. Grounding in local docs still applies to every flag of a command I ran. A suggested tool that isn't installed is marked as such.
- Updated: [vision/goals.md](../vision/goals.md), [vision/non-goals.md](../vision/non-goals.md), [pedagogy/card-format.md](../pedagogy/card-format.md).
