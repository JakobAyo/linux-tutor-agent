# 0006: Drop secret-looking lines in the hook

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
Some command lines contain secrets (`export TOKEN=…`, `curl -H "Authorization: …"`). [security/redaction.md](../security/redaction.md) already says that such lines are never used for teaching. The open question was where to drop them: in the hook, before anything is written to disk, or later in the processor, before the LLM call.

## Decision
The hook drops these lines. If a command line matches the skip list (case-insensitive glob in zsh), nothing is written to the log.

## Alternatives considered
- Filter only before the LLM call: the hook stays simpler, but secrets would sit in a plaintext log on disk.

## Consequences
- Secrets never reach the tutor's files. They stay in `~/.zsh_history`, which the tutor does not control.
- The skip list has to be a cheap zsh pattern match, with no subprocess.
- Dropped commands are invisible to the tutor, so a false positive (a harmless line that contains `token`) means a missed lesson. That's acceptable.
- The processor still masks argument values before calling the LLM ([security/redaction.md](../security/redaction.md)). The hook filter does not replace that step.
- Updated: [security/redaction.md](../security/redaction.md), [observation/shell-hooks.md](../observation/shell-hooks.md).
