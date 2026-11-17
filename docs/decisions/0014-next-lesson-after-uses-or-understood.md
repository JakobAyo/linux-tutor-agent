# 0014: Next lesson after 10 more uses or once I mark it understood

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
Each command gets a series of lessons ([ADR 0010](0010-lesson-series-per-command.md)). Something has to decide when lesson N+1 is written.

## Decision
Lesson N+1 for a command is due when either:
- I've used the command 10 more times since lesson N was written, or
- I mark lesson N as `understood`, in which case it's due right away.

The next background run writes due lessons for new commands, then up to 3 backlog lessons ([ADR 0015](0015-three-backlog-lessons-per-run.md)).

## Alternatives considered
- Only after N more uses: lessons pile up for commands I haven't studied yet.
- Only when I mark `understood`: rarely used but important commands stall if I forget to mark them.
- Only on request: no discovery without effort on my side.

## Consequences
- Commands I use a lot go deep on their own. Rare ones stay at lesson 1 until I mark them.
- The store tracks, per command, the use count when the last lesson was written.
- Updated: [pedagogy/card-format.md](../pedagogy/card-format.md).
