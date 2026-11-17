# Redaction

Default: send only the program name and flags to the LLM; mask argument values.

- `curl -H "Authorization: Bearer abc" https://x.example/api?key=…` → `curl -H <value> <url>`
- `ssh me@host` → `ssh <user@host>`

## Skip entirely
Lines containing `export`, `token`, `password`, `passwd`, `secret`, `Authorization`, `api_key`, `AWS_`, and similar. The zsh hook drops them before writing (case-insensitive glob), so they never reach disk ([ADR 0006](../decisions/0006-skip-secrets-in-hook.md)). The processor still masks argument values before every LLM call.

**TBD:** Which argument values are safe to keep because they carry meaning (e.g. unit names like `nginx` in `journalctl -u nginx`, package names, signal names)? Keep-list per command, or mask everything?

**TBD:** Is captured terminal output for "why did that fail?" redacted the same way, and is that feature opt-in?
