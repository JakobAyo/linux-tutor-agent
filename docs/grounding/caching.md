# Caching

Cards are cached so each item costs one LLM call at most.

- **Command card:** key = command name.
- **Flag card:** key = command + flag.
- **Idiom lesson:** key = idiom id.

**TBD:** Include the package version in the cache key (regenerate after a `pacman -Syu` changed the man page) or keep cards until I regenerate them manually?

**TBD:** Cache format and location: one Markdown file per card under `~/.local/share/linux-tutor/cards/`, or entries in the store? See [architecture/data-storage.md](../architecture/data-storage.md).
