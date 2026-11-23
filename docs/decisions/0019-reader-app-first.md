# 0019: Build the reader app first (M1)

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
In the M0 week I opened 5 of 99 lessons. They taught me something new, and the length was right, but I didn't read them when notified: clicking the notification did nothing, and reading meant going to the repo and running `python3 spike/process.py read`. The proposed milestone order put the UI fifth, after the foundation, parsing, detection, and grounding ([milestones/overview.md](../milestones/overview.md)).

## Decision
M1 is the reader app: a real, installable package with a command on `PATH` that opens the lesson reader from any directory, and a notification click that opens it. In M1 it reads the data the spike already writes. The spike processor keeps generating lessons until later milestones port it into the package.

## Alternatives considered
- Foundation first, then UI: cleaner order, but lessons keep piling up unread for several milestones.
- Throwaway reader in `spike/`: fastest, but the reader is the part most worth keeping, so it would be written twice.

## Consequences
- The package, its install path, and the read side of the store come first. The write side (processor, runner) follows.
- The reader has to tolerate the spike's data format, and has to be adapted when the store format is decided.
- Milestones after M1 are still open.
- Updated: [milestones/overview.md](../milestones/overview.md), [milestones/m1-reader.md](../milestones/m1-reader.md).
