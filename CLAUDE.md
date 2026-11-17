# Linux Tutor Agent

A personal tutor that teaches me Linux commands while I work normally on my Arch machine. A zsh hook records the commands I run. When a command, flag, or shell idiom is new to me, the tutor writes a short lesson (what it does, the flags I used, variations, use cases, the concept behind it) so I learn without searching the web or reading docs myself.

## Core loop
- **Observe:** a zsh `preexec` hook appends each command line (time, cwd, command) to a log; `precmd` adds the exit code. The hook only appends a line; everything else runs in the background. Never slow the shell.
- **Detect (no LLM):** split pipelines and chains, drop wrappers (`sudo`, `env`), resolve aliases with `whence -w`, compare against the known store. Three levels: new command, new flag on a known command, new shell idiom.
- **Teach (LLM):** `claude -p` writes a card from the exact command I ran, grounded in the local `man` page, `--help`, and `tldr`. Cache cards per command and per flag.
- **Track:** status `new` → `seen` → `understood` (set by me) or `dismissed`.

## Principles
- Ground every card in local docs. Arch is rolling release, and LLMs invent flags.
- Privacy first: send only the program name and flags to the LLM, mask argument values, skip lines that look like secrets (`token`, `password`, `export`, `Authorization`, …).
- Quiet by default: a counter in tmux `status-right` or `RPROMPT`, not a notification per command.
- Seed the store from `~/.zsh_history` so day one is not a flood. Ignore typos and trivial commands (`cd`, `ls`, `clear`).
- Skip basics: I have a CS background but little practical Linux experience.

## Constraints
- Auth: `claude -p` with my Claude subscription (OAuth token). No Anthropic API key. Cheap model for anything bulk, Sonnet for lessons.
- Environment: Arch Linux, Hyprland, zsh + oh-my-zsh, always inside tmux. `fzf`, `tldr`, `man`, `notify-send` installed.
- Public repo: no personal data (history, paths, tokens) in code, tests, fixtures, or docs.

## Status
Design phase, no code yet. Decided so far: docs structure, `claude -p` on the subscription, zsh hook observation, public repo with CI/CD (ADRs 0001–0004). Next: the M0 spike (`docs/milestones/m0-spike.md`).

Open questions are marked `**TBD:**` in `docs/`. Before designing or building on a topic, run `grep -rn TBD docs/`, ask me the relevant ones, then record the answer as an ADR. Never fill in a TBD by guessing.

## Commands
None yet.

## Docs
Project decisions and design notes live in `docs/`. Start at `docs/CLAUDE.md` (index).
- Record each significant decision as a new ADR in `docs/decisions/`. Don't edit an accepted ADR; supersede it.
- One responsibility per folder, one topic per file. When a file covers two things, split it.
