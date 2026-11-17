# Non-functional requirements

- **N1 Never slow the shell.** The hook only appends one line to a log (microseconds). Parsing, detection, and LLM calls run in the background.
- **N2 Privacy.** Only the program name and flags go to the LLM by default; argument values are masked; secret-looking lines are skipped. See [security/redaction.md](../security/redaction.md).
- **N3 Correct facts.** Every card is grounded in local `man`, `--help`, and `tldr` for the installed version. See [grounding/](../grounding/).
- **N4 Quiet.** No notification per command by default; a counter instead. See [ui/indicators.md](../ui/indicators.md).
- **N5 Cheap.** Detection is deterministic string matching (free). The LLM is only called to write a card, and cards are cached. See [llm/usage.md](../llm/usage.md).
- **N6 Robust.** A failure in the tutor (missing `claude`, no network, bad output) never breaks or prints into the shell.
- **N7 Public-repo safe.** No personal data (history, paths, tokens) in code, tests, fixtures, or docs.

**TBD:** Concrete budgets: max hook latency (e.g. < 5 ms), max LLM calls or cost per day, card generation latency target?
