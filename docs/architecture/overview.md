# Architecture overview

```
zsh preexec/precmd ──append──▶ cmds.log
                                  │  (background trigger)
                                  ▼
                      parser ─▶ redactor ─▶ detector ◀──▶ store
                                               │ new item
                                               ▼
                       grounding (man/--help/tldr/pacman) ─▶ teacher (claude -p) ─▶ card cache
                                                                                       │
                              counter (tmux/RPROMPT) · TUI · zle widgets ◀─────────────┘
```

1. **Observe:** the hook appends a line ([observation/](../observation/)).
2. **Parse and redact:** split, resolve, mask ([observation/command-parsing.md](../observation/command-parsing.md), [security/redaction.md](../security/redaction.md)).
3. **Detect:** compare with the store ([detection/](../detection/)).
4. **Teach:** ground and write the card ([grounding/](../grounding/), [llm/](../llm/)).
5. **Show:** quiet counter and on-demand surfaces ([ui/](../ui/)).
