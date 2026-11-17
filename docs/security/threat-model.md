# Threat model

## Assets
- Shell history and the live command log: may contain emails, hostnames, private paths, tokens, URLs with keys, passwords typed as arguments.
- Captured terminal output (for "why did that fail?"): may contain anything on screen.
- The Claude OAuth token, if stored by the tool.

## Where data can go
| Flow | Risk | Mitigation |
|---|---|---|
| Prompt to `claude -p` | Secrets sent to Anthropic | [redaction.md](redaction.md) |
| Local store and logs | Readable by other users or backups | [data-handling.md](data-handling.md) |
| Public repo (tests, fixtures, docs, issues) | My history published | Synthetic fixtures only; CI secret scanning ([ci-cd/supply-chain.md](../ci-cd/supply-chain.md)) |
| Bug reports from users | Users paste their history | Issue template warns to redact |

## Other risks
- The tutor runs `<cmd> --help` for grounding: a program that ignores `--help` could do real work. See [grounding/local-docs.md](../grounding/local-docs.md).
- The hook runs in every shell: a bug must not break or slow the shell.
