# 0017: Use the develop + main branch model

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
The repo is public with CI/CD ([ADR 0004](0004-public-repo.md)). [ci-cd/git-workflow.md](../ci-cd/git-workflow.md) left open whether to use a `develop` + `main` model or trunk-based development (`main` only). The spike work lived on a `spike` branch.

## Decision
Use `develop` + `main`. Day-to-day work goes on feature branches off `develop`, and PRs into `develop` are squash-merged. `main` only receives `develop` through a merge commit at release time. The `spike` branch was renamed to `develop`.

## Alternatives considered
- Trunk-based (`main` only, squash-merged PRs): simpler, but every merge lands on the public default branch, including spike and half-finished work.

## Consequences
- `main` stays stable and release-ready. Unfinished work stays on `develop`.
- Branch protection for `main` and `develop` still has to be set up on GitHub.
- Updated: [ci-cd/git-workflow.md](../ci-cd/git-workflow.md).
