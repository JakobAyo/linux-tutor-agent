# Seeding

Import `~/.zsh_history` (extended format, ~465 distinct first words) into the store as a **learning backlog** ([ADR 0008](../decisions/0008-history-as-learning-backlog.md)). Much of the history is copy-pasted, so neither "in history" nor "used often" means known.

## Plan
1. Parse the history with the same parser as live commands ([observation/command-parsing.md](../observation/command-parsing.md)).
2. Store every command, flag, and idiom found as `new`, with its use count.
3. Rank the backlog by use count, most used first.
4. Generate cards a few at a time, not all at once. The first-day flood is avoided by pacing, not by marking items as known.
5. Optional triage: dismiss items I don't care about. Only I set `understood` or `dismissed`.

**TBD:** Pacing: how many backlog cards per processor run or per day, or only when I open an item? (See [llm/usage.md](../llm/usage.md).)

**TBD:** Triage UI for dismissing: a TUI screen, an fzf multi-select, or a plain file I edit?
