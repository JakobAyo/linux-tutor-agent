# Novelty levels

Detection is deterministic string matching against the known store. No LLM is called to detect; the LLM only writes the card.

| Level | Example | Result |
|---|---|---|
| New command | `journalctl` the first time | Full command card |
| New flag on a known command | `journalctl -b -1` when `journalctl` is known | Small card for that flag only |
| New shell idiom | `<(…)`, `$(…)`, `2>&1`, `xargs -0`, here-strings | Concept lesson |

## Arch extras
- `pacman -Qo "$(command -v cmd)"` gives the owning package.
- `pacman -Qi <pkg>` gives the package description.

**TBD:** When is something "new": the first time it's seen, or only after N uses (to skip one-offs)?

**TBD:** Does a flag combination (`-xeu`) count as one item or as three single flags?

**TBD:** Initial list of shell idioms to detect, and how they're matched (regex list vs. parser output)?
