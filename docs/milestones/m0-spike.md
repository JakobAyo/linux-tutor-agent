# M0: Spike

Status: Planned.

## Goal
Find out in one evening whether automatic command cards are worth building, then use them for a week.

## Scope
- The `preexec`/`precmd` hook writes one JSON line per command and drops secret-looking lines ([observation/shell-hooks.md](../observation/shell-hooks.md), ADRs [0005](../decisions/0005-log-line-format.md), [0006](../decisions/0006-skip-secrets-in-hook.md)).
- A throwaway script that I run by hand ([ADR 0007](../decisions/0007-manual-processor-in-spike.md)): it reads new lines, finds commands not seen before (first word only, after dropping `sudo`), and writes one Markdown card per new command using `man`, `--help`, and `tldr` as grounding, via `claude -p`.
- Seed `~/.zsh_history` as a backlog ranked by use count. Each run also writes cards for the top few backlog commands ([ADR 0008](../decisions/0008-history-as-learning-backlog.md)).
- Throwaway code lives in `spike/`.

## Done when
- [ ] Hook installed and logging without noticeable delay.
- [ ] Cards generated for new commands, with no invented flags in a manual check of 10 cards.
- [ ] Used for a week; results written below.

## Questions the spike should answer
- Do I actually read the cards?
- Are the cards correct and useful at this length?
- Push or pull? ([ui/surfaces.md](../ui/surfaces.md))

## Results
TBD (after the spike week).
