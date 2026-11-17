# Seeding

Avoid a first-day flood: before the tutor goes live, import `~/.zsh_history` (extended format, ~465 distinct first words) into the store.

## Plan
1. Parse the history with the same parser as live commands ([observation/command-parsing.md](../observation/command-parsing.md)).
2. Mark all found commands, flags, and idioms with an initial status.
3. One triage pass: I pick which seeded items I actually want to learn.

**TBD:** Initial status for seeded items: `seen` (assume familiar) or a separate "known" marker? And should frequency matter (used 50× = known, used once = maybe learn)?

**TBD:** Triage UI: a TUI screen, an fzf multi-select, or a plain file I edit?
