# Glossary

- **Card:** a short lesson generated for one item, based on the exact command I ran.
- **Command card / flag card / idiom lesson:** the three card types, one per novelty level.
- **Concept:** a mechanism behind several commands (e.g. journald behind `journalctl` and `dmesg`).
- **Grounding:** local docs (man, `--help`, tldr, pacman) put into the prompt so the LLM can't invent flags.
- **Hook:** the zsh `preexec`/`precmd` functions that append command lines to the log.
- **Idiom:** a shell construct worth learning on its own (`2>&1`, `<(…)`, `$(…)`, here-strings, `xargs -0`).
- **Item:** anything the store tracks: a command, a flag of a command, or an idiom.
- **Novelty level:** whether an item is a new command, a new flag on a known command, or a new idiom.
- **Redaction:** masking argument values and skipping secret lines before anything reaches the LLM.
- **Seeding:** importing `~/.zsh_history` into the store so known commands don't produce cards.
- **Status:** `new` → `seen` → `understood`, or `dismissed`.
- **Store:** the local memory of items and their status.
