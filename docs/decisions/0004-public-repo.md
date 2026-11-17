# 0004: Public repository with CI/CD

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The project will be published as a public repo. The tool handles shell history, which is sensitive.

## Decision
The repo is public, with CI/CD from the start: quality gates on every PR, automated releases, and supply-chain hardening.

## Alternatives considered
- Private repo, publish later: less up-front work, but retrofitting CI and scrubbing history later is harder.

## Consequences
- No personal data (history, paths, tokens) in code, tests, fixtures, docs, or commit history ([security/threat-model.md](../security/threat-model.md)).
- CI never has a Claude token; tests use a fake `claude` ([ci-cd/testing-strategy.md](../ci-cd/testing-strategy.md)).
- Needs `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `.github/` config ([community/](../community/)).
