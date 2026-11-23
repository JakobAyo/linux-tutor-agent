# M0: Spike

Status: Done (2026-11-23).

## Goal
Find out whether automatic discovery lessons are worth building, then use them for a week.

## Scope
- The `preexec`/`precmd` hook writes one JSON line per command and drops secret-looking lines ([observation/shell-hooks.md](../observation/shell-hooks.md), ADRs [0005](../decisions/0005-log-line-format.md), [0006](../decisions/0006-skip-secrets-in-hook.md)).
- A throwaway processor that reads new lines, finds commands not seen before (first word only, after dropping `sudo`), and writes Markdown lessons via `claude -p`, grounded in `man` (including subcommand pages like `git-branch`) and `tldr`.
- Lessons are discovery lessons in a series per command (ADRs [0009](../decisions/0009-discovery-lessons.md), [0010](../decisions/0010-lesson-series-per-command.md)).
- It started as a manual run ([ADR 0007](../decisions/0007-manual-processor-in-spike.md)). Now `precmd` starts it in the background, debounced to 10 minutes, and it sends one notification per run ([ADR 0011](../decisions/0011-activity-debounced-trigger.md), [0012](../decisions/0012-eager-lessons-without-daily-cap.md), [0013](../decisions/0013-notify-when-lessons-are-ready.md)).
- Seed `~/.zsh_history` as a backlog ranked by use count. Each run also writes lessons for the top few backlog commands ([ADR 0008](../decisions/0008-history-as-learning-backlog.md)).
- Throwaway code lives in `spike/`.

## Done when
- [x] Hook installed and logging without noticeable delay.
- [x] Lessons generated automatically in the background. The manual check of 10 lessons for invented flags was skipped. Invented flags get reported as bugs when I notice them ([ADR 0018](../decisions/0018-close-m0-without-manual-flag-check.md)).
- [x] Used for a week; results written below.

## Questions the spike should answer
- Do I actually read the lessons when notified?
- Do the lessons teach me something new (flags, combos, tools), at this length?
- Is a series per command useful, and when should the next lesson come?

## Findings so far
- Commands with subcommands (`git`, `pacman`, `systemctl`, `npm`) were grounded in only one man page, so flags from other subcommands showed up as "unverified" and were explained from memory. The spike now sends up to 3 subcommand pages (`git-rebase`), most used first. Still to check: whether that removes most "unverified" flags.

## Results
Week of 2026-11-17 to 2026-11-23: 447 commands logged, 104 lessons for 99 commands, about $4 in total.

- **Do I read the lessons when notified?** No. I opened 5 of 99. Clicking the notification did nothing, and reading meant going to the repo and running `python3 spike/process.py read`. Reading, not writing, is the bottleneck.
- **Do they teach me something new, at this length?** Yes. The ones I read taught me something, and the length was right.
- **Is a series per command useful?** Not enough data yet. Almost no command reached lesson 2.
- **Grounding:** 37 of 104 lessons carry an "Unverified flags" note. Not checked by hand ([ADR 0018](../decisions/0018-close-m0-without-manual-flag-check.md)).

Next: M1 builds the reader app so lessons can be opened from anywhere and from the notification ([ADR 0019](../decisions/0019-reader-app-first.md)).
