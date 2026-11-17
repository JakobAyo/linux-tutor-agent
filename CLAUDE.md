# Linux Tutor Agent

A personal tutor that teaches me Linux while I work normally on my Arch machine. A zsh hook records the commands I run. In the background, the tutor writes discovery lessons anchored to those commands: flags I haven't used, real use cases, combinations with other commands, related or better tools, and the concept behind them. Commands I keep using get a series of lessons that go deeper each time. The goal is continuous learning, not a personal `tldr`: over time I become comfortable doing everything in the terminal and writing my own scripts and automations.

## Core loop
- **Observe:** a zsh `preexec` hook appends each command line (time, cwd, command) to a log; `precmd` adds the exit code. The hook only appends a line; everything else runs in the background. Never slow the shell.
- **Detect (no LLM):** split pipelines and chains, drop wrappers (`sudo`, `env`), resolve aliases with `whence -w`, compare against the known store. Three levels: new command, new flag on a known command, new shell idiom.
- **Trigger:** `precmd` starts the processor in the background (`&!`, lock file) at most every 10 minutes per shell. It exits at once when there's nothing new.
- **Teach (LLM):** `claude -p` writes a discovery lesson from the exact command I ran, grounded in the local `man` pages (including subcommand pages) and `tldr`. Lessons are eager, with no daily cap, and cached per command + lesson number.
- **Notify:** one `notify-send` per run that wrote lessons, naming the commands.
- **Track:** status `new` → `seen` → `understood` (set by me) or `dismissed`.

## Principles
- Ground every flag in local docs. Arch is rolling release, and LLMs invent flags.
- Privacy first: send only the program name and flags to the LLM, mask argument values, skip lines that look like secrets (`token`, `password`, `export`, `Authorization`, …).
- Never a storm: at most one notification per processor run, never one per command.
- Seed the store from `~/.zsh_history` so day one is not a flood. Ignore typos and trivial commands (`cd`, `ls`, `clear`).
- Skip basics: I have a CS background but little practical Linux experience.

## Constraints
- Auth: `claude -p` with my Claude subscription (OAuth token). No Anthropic API key. Cheap model for anything bulk, Sonnet for lessons.
- Environment: Arch Linux, Hyprland, zsh + oh-my-zsh, always inside tmux. `fzf`, `tldr`, `man`, `notify-send` installed.
- Public repo: no personal data (history, paths, tokens) in code, tests, fixtures, or docs.

## Status
M0 spike in progress (`spike/`, `docs/milestones/m0-spike.md`). Decided so far: docs structure, `claude -p` on the subscription, zsh hook observation, public repo with CI/CD, JSONL log written in `precmd`, secrets dropped in the hook, history seeded as a learning backlog (ADRs 0001–0008), discovery lessons in a series per command, an activity-debounced background trigger, eager lessons with no daily cap, one notification per run (ADRs 0009–0013), next lesson after 10 more uses or `understood`, 3 backlog lessons per run, notifications only with no counter (ADRs 0014–0016), `develop` + `main` branch model (ADR 0017).

Open questions are marked `**TBD:**` in `docs/`. Before designing or building on a topic, run `grep -rn TBD docs/`, ask me the relevant ones, then record the answer as an ADR. Never fill in a TBD by guessing.

## Commands
None yet.

## Docs
Project decisions and design notes live in `docs/`. Start at `docs/CLAUDE.md` (index).
- Record each significant decision as a new ADR in `docs/decisions/`. Don't edit an accepted ADR; supersede it.
- One responsibility per folder, one topic per file. When a file covers two things, split it.
