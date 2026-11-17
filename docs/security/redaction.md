# Redaction

Default: send only the program name and flags to the LLM; mask argument values.

- `curl -H "Authorization: Bearer abc" https://x.example/api?key=…` → `curl -H <value> <url>`
- `ssh me@host` → `ssh <user@host>`

## Skip entirely
Lines containing `export`, `token`, `password`, `passwd`, `secret`, `Authorization`, `api_key`, `AWS_`, and similar. They are never logged for teaching.

**TBD:** Skip such lines already in the hook (never written to disk) or only before sending to the LLM?

**TBD:** Which argument values are safe to keep because they carry meaning (e.g. unit names like `nginx` in `journalctl -u nginx`, package names, signal names)? Keep-list per command, or mask everything?

**TBD:** Is captured terminal output for "why did that fail?" redacted the same way, and is that feature opt-in?
