# Learner model

Status model:

| Status | Meaning | Set by |
|---|---|---|
| `new` | Detected, card not opened yet | Detector |
| `seen` | Card opened at least once | Tutor (on open) |
| `understood` | I can explain and use it | Me |
| `dismissed` | Not worth learning | Me |

The store holds commands, flags (under their command), and idioms, each with a status, first-seen time, use count, and the example command line (redacted).

**TBD:** Can an item go back from `understood` to `new` (e.g. after failing a recall question or not using it for months)?

**TBD:** Is a flag's status independent of its command's status?
