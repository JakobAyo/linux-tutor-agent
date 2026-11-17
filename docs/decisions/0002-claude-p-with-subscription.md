# 0002: Use `claude -p` with the Claude subscription, no API key

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The tutor needs an LLM to write cards. I have a Claude subscription and the Claude Code CLI, but no Anthropic API key.

## Decision
All LLM calls go through `claude -p` (print mode), authenticated with my Claude subscription (OAuth). No Anthropic SDK or API key.

## Alternatives considered
- Anthropic API with an API key: not available to me, and adds billing.
- A local model: no setup cost per call, but weaker cards and heavy on the machine.

## Consequences
- Calls are subject to subscription rate limits; caching and deterministic detection keep usage low ([llm/usage.md](../llm/usage.md)).
- The runner must isolate calls (no tools, neutral directory) ([llm/runner.md](../llm/runner.md)).
- Users of the public repo need Claude Code installed and logged in.
- Open: how background jobs authenticate (TBD in [llm/runner.md](../llm/runner.md)).
