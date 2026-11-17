# Command parsing

Turns one logged command line into the items detection compares against the store.

## Steps
1. **Split** on `|`, `&&`, `||`, `;` (respecting quotes and subshells).
2. **Drop wrappers:** `sudo`, `env`, `nice`, `time`, `command`, `exec`, and similar; keep the real program.
3. **Resolve aliases and functions** with `whence -w` / `whence -v`. oh-my-zsh aliases (e.g. git plugin `gst`, `gco`) must map to the real command (`git status`, `git checkout`).
4. **Extract flags:** short (`-xeu` → `-x -e -u`), long (`--since`), and subcommands (`git rebase`, `systemctl status`).
5. **Extract idioms:** process substitution `<(…)`, command substitution `$(…)`, redirections `2>&1`, here-strings `<<<`, `xargs -0`, etc.

## Notes
- Alias resolution needs the user's live zsh environment. The log is written from the shell, so the hook could log the resolved form, or the parser could run `zsh -ic 'whence -w …'` later.

**TBD:** Resolve aliases at hook time (in the shell, cheap with `whence`, but adds work to the hook) or later in the background (needs an interactive zsh to load aliases)?

**TBD:** Parser implementation: a hand-written tokenizer, Python `shlex`, or a real shell parser (e.g. `bashlex`, tree-sitter-bash)? zsh syntax differs from bash in places.

**TBD:** Are subcommands (`git rebase`, `systemctl mask`) treated as separate commands or as "flags" of the parent?
