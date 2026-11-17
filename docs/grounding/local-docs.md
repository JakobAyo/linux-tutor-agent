# Local docs

LLMs invent flags, and Arch is a rolling release, so the locally installed docs are the only reliable source for the installed version. Every card prompt includes them.

| Source | Command | Use |
|---|---|---|
| man page | `MANWIDTH=… man <cmd> \| col -b` | Authoritative flags and semantics |
| `--help` | `<cmd> --help` | Short flag list, often more current than man |
| tldr page | `tldr <cmd>` | Practical example variations |
| Package | `pacman -Qo "$(command -v cmd)"`, `pacman -Qi <pkg>` | Owning package and its description |
| Man search | `whatis`, `apropos` / `man -k` | One-line summary, related commands |

## Rules
- Prefer man for facts, tldr for examples.
- If no local doc exists, say so on the card instead of guessing.

**TBD:** How to trim long man pages (e.g. `bash`, `zsh`, `systemctl` are huge) to fit the prompt: only the sections for the flags I used, a size cap, or a pre-extracted flag table?

**TBD:** Is running `<cmd> --help` safe for every command? Some programs ignore `--help` and do real work. Allowlist only, or skip `--help` for commands without a man page?

**TBD:** Should the card link to the Arch Wiki page (URL only, not fetched)?
