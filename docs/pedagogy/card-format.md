# Card format

A card starts from the exact command I ran, then generalizes. Example of a command card:

```
journalctl  (package: systemd)
You ran: journalctl -xeu nginx
  -x  add explanations   -e  jump to end   -u  one unit only
Variations
  journalctl -b -1 -p err        errors from the previous boot
  journalctl -fu sshd            follow a service live
  journalctl --since "1 hour ago"
  journalctl --vacuum-size=500M  shrink the log store
Concept: journald keeps binary logs per boot; units are services managed by systemd.
Related: systemctl status, dmesg · man journalctl · Arch Wiki: Systemd/Journal
```

## Card types
- **Command card:** package, what it does, my flags explained, 3–5 variations with use cases, the concept, related commands and docs.
- **Flag card:** one flag of a known command, what it does, one or two variations.
- **Idiom lesson:** the shell mechanism (e.g. file descriptors for `2>&1`), my example, variations.

## Principles
- Short. Skip basics.
- Explain *why* and the concept, not only syntax.
- Dangerous commands (`dd`, `rm -rf`, `chmod -R`) get an explicit warning.

**TBD:** Output format: Markdown files (spike), plain text for the terminal, or rich text in a TUI?
