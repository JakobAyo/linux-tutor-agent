# Noise filter

Things that should not create a card:

- **Typos:** command not found (exit code 127) or no binary on `$PATH`.
- **Trivial commands:** `cd`, `ls`, `clear`, `exit`, `pwd`, … (an ignore list).
- **One-off scripts:** `./build.sh`, paths into project directories.
- **Secret-looking lines:** skipped entirely before anything else ([security/redaction.md](../security/redaction.md)).

**TBD:** Is the ignore list fixed, user-configurable, or learned (e.g. auto-ignore anything I `dismiss`)?

**TBD:** How are local scripts and project binaries (`./x`, `~/bin/x`, `node_modules/.bin/x`) told apart from real system commands? (Idea: only commands owned by a pacman package, via `pacman -Qo`.)
