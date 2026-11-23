# M1: Reader app

Status: In progress.

## Goal
Make the lessons easy to open, so I actually read them. In the M0 week I opened 5 of 99 ([m0-spike.md](m0-spike.md), [ADR 0019](../decisions/0019-reader-app-first.md)).

## Scope
- A Python package managed with uv, installed system-wide with `uv tool install --editable .`. It puts `shtutor` on `PATH` ([ADRs 0020](../decisions/0020-python-with-uv.md), [0022](../decisions/0022-command-name-shtutor.md)).
- `shtutor` opens a Textual TUI from any directory ([ADR 0021](../decisions/0021-textual-tui-reader.md)):
  - a list of commands with waiting lessons, unread first;
  - a lesson view that renders the Markdown, with the earlier lessons of the series one key away;
  - keys to mark a command `understood` or `dismissed`. Opening a lesson marks it `seen`.
- It reads the spike's data in `~/.local/share/linux-tutor-spike/` and writes status changes to its `store.json` under the same lock (`store.lock`) as the spike, with the same meaning (`understood` makes the next lesson due, [ADR 0014](../decisions/0014-next-lesson-after-uses-or-understood.md)).
- The spike's notification gets a click action that opens `shtutor` ([ADR 0016](../decisions/0016-notifications-only-no-counter.md)). The notification daemon (quickshell) supports actions.

## Out of scope
- Porting the processor, hook, or grounding into the package. The spike keeps generating lessons.
- CI, releases, and packaging for others.
- zle widgets.

## Done when
- [x] `shtutor` opens the reader from any directory.
- [x] Clicking a lesson notification opens the reader.
- [x] Status changes made in the reader are picked up by the next spike run.
- [ ] Used for a week; results written below.

## Questions M1 should answer
- Do I read the lessons now? (Compare the `seen`/`understood` count with M0's 5 of 99.)
- Is the notification the main way I open it, or do I open it myself?

## Results
TBD (after the M1 week).
