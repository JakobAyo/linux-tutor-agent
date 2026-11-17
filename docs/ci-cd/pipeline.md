# CI pipeline

GitHub Actions on every PR and push. The same checks run locally via pre-commit.

| Job | Checks |
|---|---|
| lint | `ruff check`, `ruff format --check` |
| types | `mypy` (strict on `src`) |
| test | `pytest` with a fake `claude` (no real calls, no secrets), coverage floor |
| shell | `zsh -n` syntax check and `shellcheck` (where applicable) on hook and widget scripts |
| security | CodeQL, secret scanning, dependency review ([supply-chain.md](supply-chain.md)) |
| pr-policy | PR title is a Conventional Commit ([git-workflow.md](git-workflow.md)) |

Tools assume Python; adjust if the stack decision changes ([architecture/tech-stack.md](../architecture/tech-stack.md)).

**TBD:** Coverage floor (e.g. 90%)? Python version matrix (3.12 only, or 3.12–3.14)? Test on an Arch container (`archlinux:latest`) so man/tldr/pacman behave like the real target?
