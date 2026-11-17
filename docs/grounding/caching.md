# Caching

Cards are cached so each lesson costs one LLM call at most.

- **Command lesson:** key = command name + lesson number ([ADR 0010](../decisions/0010-lesson-series-per-command.md)). The store also keeps a short summary of what each lesson taught, so the next one builds on it.
- **Flag card:** key = command + flag.
- **Idiom lesson:** key = idiom id.

**TBD:** Include the package version in the cache key (regenerate after a `pacman -Syu` changed the man page) or keep cards until I regenerate them manually?

**TBD:** Cache format and location: one Markdown file per card under `~/.local/share/linux-tutor/cards/`, or entries in the store? See [architecture/data-storage.md](../architecture/data-storage.md).
