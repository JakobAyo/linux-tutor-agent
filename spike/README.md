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

That's it. The hook starts the processor in the background, so lessons appear on their own.

## How it runs
- `precmd` starts `process.py run --auto` disowned, at most every 10 minutes per shell, and on the first prompt of a new shell ([ADR 0011](../docs/decisions/0011-activity-debounced-trigger.md)). A lock file keeps it to one run at a time across shells.
- Each run writes lesson 1 for every new command, the next lesson for every command that's due, and up to 3 lessons from the history backlog, most used first ([ADRs 0012](../docs/decisions/0012-eager-lessons-without-daily-cap.md), [0015](../docs/decisions/0015-three-backlog-lessons-per-run.md)).
- The next lesson for a command is due after 10 more uses, or right away once you mark it `understood` ([ADR 0014](../docs/decisions/0014-next-lesson-after-uses-or-understood.md)).
- A run that wrote lessons sends one notification, e.g. "3 new lessons: rsync, find, git (2)" ([ADR 0013](../docs/decisions/0013-notify-when-lessons-are-ready.md)).
- If `claude -p` fails (rate limit, auth), the run stops and the rest stays due for the next run. Check `run.log`.

Set `LTUTOR_SPIKE_AUTO=0` before sourcing the hook to only log, or `LTUTOR_SPIKE_INTERVAL=<seconds>` to change the debounce.

## Daily use
```sh
python3 spike/process.py read         # fzf picker, opens the latest lesson, marks it seen
python3 spike/process.py read --all   # also older lessons in a series
python3 spike/process.py mark git understood   # next git lesson in the next run
python3 spike/process.py mark git dismissed    # no more git lessons
python3 spike/process.py list [new|seen|understood|dismissed]
python3 spike/process.py lesson grep find      # next lesson for these commands now
python3 spike/process.py run                   # a run in the foreground, with output
```

Start a command with a space to keep it out of the log.

Every part of a pipeline or chain counts (`journalctl -b | grep -i err` counts `journalctl` and `grep`).
Alias-added flags (oh-my-zsh's `grep --color=auto ...`) are ignored, so lessons start from what you typed.
A lesson gets your top 5 usage patterns, the flags you've used, how often you pipe into the command, and a summary of what earlier lessons in the series taught.
After a parser change, run `seed --force` to recount from history. It keeps statuses and lessons.

## Data
Everything lives in `~/.local/share/linux-tutor-spike/` (override with `LTUTOR_SPIKE_DIR`):
`cmds.log` (hook output), `offset`, `store.json`, `lessons/<cmd>/<n>.md`, `usage.jsonl` (time and cost per lesson), `run.log` (background runs), and the lock files `run.lock`, `store.lock`.
`cards/` holds the tldr-style cards from before the lesson series. They don't count as lessons.
Delete the directory to start over.

## Spike-only defaults
These are placeholders, not decisions. The matching `TBD`s in `docs/` stay open until the spike results are in.

| Open question | Spike default |
|---|---|
| Is `<cmd> --help` safe to run? | Never run it. Grounding is `man`, `tldr -m`, `whatis`, and `pacman -Qo`/`-Qi`. |
| How to trim huge man pages | 60k chars in total. Up to 3 subcommand pages (`git-rebase`), most used first, 15k chars each. The main page gets the rest. A page over its cap is cut to its head plus the option entries for the flags used. |
| Model per lesson | Sonnet for every lesson. |
| Data directory name | `linux-tutor-spike`, separate from the final name. |
| Which argument values to keep | Flags are kept. Values become `<arg>`/`<value>`. The first plain word is kept only if the local docs mention it (a subcommand like `git rebase`). |
| Detection depth | Lessons per command. Flags are counted and fed into the lesson, but a new flag doesn't trigger a lesson of its own. |
| Background auth | `claude -p` runs from your shell's environment, so it uses your normal login. |

## Known limits
- Commands inside `$(...)`, `find -exec`, and `xargs` arguments aren't detected.
- `tldr` may download a page the first time it's looked up (sends the command name to the tldr page source).
- Lessons with flags of the command that the docs never mention get an **Unverified flags** note at the bottom. That supports the manual 10-lesson check; it doesn't replace it. Flags of *related* tools aren't checked.
- Related tools that aren't on `PATH` are marked *(not installed)*.
