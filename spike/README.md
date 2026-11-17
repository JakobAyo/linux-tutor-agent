# M0 spike

Throwaway code for [docs/milestones/m0-spike.md](../docs/milestones/m0-spike.md). Python stdlib only, no install.

## Setup
1. Add the hook at the **end** of `~/.zshrc`, then open a new shell:
   ```zsh
   source /path/to/linux-tutor-agent/spike/hook.zsh
   ```
2. Seed the backlog from `~/.zsh_history` (once):
   ```sh
   python3 spike/process.py seed
   ```

## Daily use
```sh
python3 spike/process.py run          # cards for new commands + top 3 backlog commands
python3 spike/process.py run -b 0     # only new commands
python3 spike/process.py read         # fzf picker, opens the card, marks it seen
python3 spike/process.py mark git understood   # or dismissed
python3 spike/process.py list [new|seen|understood|dismissed]
```

Start a command with a space to keep it out of the log.

## Data
Everything lives in `~/.local/share/linux-tutor-spike/` (override with `LTUTOR_SPIKE_DIR`):
`cmds.log` (hook output), `offset`, `store.json`, `cards/<cmd>.md`, `usage.jsonl` (time and cost per card).
Delete the directory to start over.

## Spike-only defaults
These are placeholders, not decisions. The matching `TBD`s in `docs/` stay open until the spike results are in.

| Open question | Spike default |
|---|---|
| Is `<cmd> --help` safe to run? | Never run it. Grounding is `man`, `tldr -m`, `whatis`, and `pacman -Qo`/`-Qi`. |
| How to trim huge man pages | Above 30k chars: the first 8k chars plus the option entries for the flags used. |
| Model per card | Sonnet for every card. |
| Data directory name | `linux-tutor-spike`, separate from the final name. |
| Which argument values to keep | Flags are kept. Values become `<arg>`/`<value>`. The first plain word is kept only if the local docs mention it (a subcommand like `git rebase`). |
| Detection depth | First word only, as the spike plan says. Flag counts are recorded but don't trigger cards. |

## Known limits
- Commands inside `$(...)`, `find -exec`, and `xargs` arguments aren't detected.
- `tldr` may download a page the first time it's looked up (sends the command name to the tldr page source).
- Cards with flags the docs never mention get an **Unverified flags** note at the bottom. That supports the manual 10-card check; it doesn't replace it.
