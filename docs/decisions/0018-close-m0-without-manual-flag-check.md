# 0018: Close M0 without the manual flag check

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
M0 was "done when" a manual check of 10 lessons found no invented flags ([milestones/m0-spike.md](../milestones/m0-spike.md)). After about a week of use there are 104 lessons, and 37 of them carry an automatic "Unverified flags" note. I don't have time for the manual check now, and the spike has already answered its main question: the bottleneck is reading the lessons, not writing them.

## Decision
Skip the manual 10-lesson check. Close M0 with the results gathered so far. When I notice an invented flag while reading, I report it as a bug (a GitHub issue with the lesson and the flag).

## Alternatives considered
- Do the check before moving on: it blocks the work that fixes the real problem (lessons go unread) for a check whose outcome doesn't change what's built next.

## Consequences
- How well lessons are grounded is measured from bug reports during real use, not from a sample.
- The "Unverified flags" note stays in lessons as the automatic signal.
- Updated: [milestones/m0-spike.md](../milestones/m0-spike.md).
