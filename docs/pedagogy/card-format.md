# Card format

A lesson starts from the exact command I ran, then teaches what I probably don't know yet ([ADR 0009](../decisions/0009-discovery-lessons.md)). It is a discovery lesson, not a personal `tldr`.

Example, lesson 1 for `rsync`:

```
rsync — lesson 1  (package: rsync)
You ran: rsync -av <src> <dst>
  -a  archive: recursive, keeps perms/times/links   -v  list files
What you're missing
  -n / --dry-run         preview before a destructive sync
  --delete               make dst an exact mirror (pair with -n first!)
  -P                     progress + resume partial files over slow links
Use cases
  rsync -avP <dir> host:<dir>        copy over ssh, resumable
  rsync -aHAX --delete / <backup>/   full system backup that keeps ACLs/xattrs
Combine it
  find ... -newer <ref> -print0 | rsync -a --files-from=- --from0 ...
Related tool: rclone (cloud remotes) · not installed
Concept: delta transfer, only changed blocks cross the wire
Next lesson: --link-dest snapshots, filter rules
```

## Lesson series
Each command gets a series of lessons ([ADR 0010](../decisions/0010-lesson-series-per-command.md)). Every lesson knows what earlier ones taught and goes one level deeper, e.g. `rsync`: 1 core flags and use cases → 2 `--link-dest` snapshots, filters, over ssh → 3 a backup script on a systemd timer.

**TBD:** When is the next lesson in a series due: after N more uses of the command since the last lesson, after I mark the previous one `understood`, only when I ask, or a mix?

## Lesson types
- **Command lesson:** my usage, the flags I used, flags and modes I'm missing with use cases, combinations with other commands, related or better tools (marked if not installed), the concept, a teaser for the next lesson.
- **Flag card:** one flag of a known command, what it does, one or two variations.
- **Idiom lesson:** the shell mechanism (e.g. file descriptors for `2>&1`), my example, variations.

## Principles
- Skip basics. Spend the space on what I don't know yet.
- Explain *why* and the concept, not only syntax.
- Prefer realistic use cases and combinations that point toward scripting and automation.
- Dangerous commands (`dd`, `rm -rf`, `chmod -R`, `rsync --delete`) get an explicit warning.

**TBD:** Output format: Markdown files (spike), plain text for the terminal, or rich text in a TUI?
