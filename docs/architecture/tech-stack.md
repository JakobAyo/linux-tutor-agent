# Tech stack

| Part | Choice | Status |
|---|---|---|
| Hook and widgets | zsh | Decided ([ADR 0003](../decisions/0003-zsh-hook-observation.md)) |
| LLM | `claude -p` on the Claude subscription | Decided ([ADR 0002](../decisions/0002-claude-p-with-subscription.md)) |
| Core | Python 3.12+ with uv | TBD |
| TUI | Textual | TBD |
| Background jobs | systemd user units or `&!` | TBD ([operations/background-jobs.md](../operations/background-jobs.md)) |
| Quality tools | ruff, mypy (strict), pytest, shellcheck / `zsh -n` | TBD ([ci-cd/pipeline.md](../ci-cd/pipeline.md)) |

**TBD:** Confirm Python 3.12+ with uv vs. another language (e.g. Go or Rust for a single static binary, nicer for an AUR package)?
