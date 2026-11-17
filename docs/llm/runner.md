# Runner

The tutor calls Claude through the Claude Code CLI in print mode, `claude -p`, authenticated with my Claude subscription (OAuth). There is no Anthropic API key ([ADR 0002](../decisions/0002-claude-p-with-subscription.md)).

## Rules
- No tools: the model only writes text.
- Run in a neutral working directory so no project `CLAUDE.md` or settings leak into the call.
- Prompt in, card out; the runner never acts on the output.
- Timeouts, and failures never surface in the shell.

**TBD:** Model per task: Sonnet for command cards and concept lessons, a cheaper model (Haiku) for flag cards? Configurable in a settings file?

**TBD:** Auth in background jobs: does `claude -p` pick up the login from `~/.claude` in a systemd user unit, or does it need a long-lived token (`claude setup-token`, `CLAUDE_CODE_OAUTH_TOKEN`) stored in the data directory?
