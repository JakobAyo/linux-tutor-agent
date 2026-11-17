# M0: Spike

Status: Planned.

## Goal
Find out in one evening whether automatic command cards are worth building, then use them for a week.

## Scope
- The `preexec` hook appends to a log ([observation/shell-hooks.md](../observation/shell-hooks.md)).
- A throwaway script: read new lines, find commands not seen before (first word only, after dropping `sudo`), and write one Markdown card per new command using `man`, `--help`, and `tldr` as grounding, via `claude -p`.
- Seed from `~/.zsh_history` so existing commands don't produce cards.
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
