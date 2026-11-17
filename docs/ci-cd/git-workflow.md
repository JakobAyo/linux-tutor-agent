# Git workflow

Proposed, following `../tutor-agent` (its ADR 0033):

- Feature branches off `develop`. PRs into `develop` are squash-merged; the PR title must be a Conventional Commit (it drives the version and the CHANGELOG).
- `develop` → `main` with a merge commit; release-please then opens a release PR ([release.md](release.md)).
- Branch protection on `main` and `develop`: required checks, no force push.
- Never edit `CHANGELOG.md` or the version by hand.

**TBD:** Adopt the `develop` + `main` model, or simpler trunk-based (`main` only, squash-merged PRs)? The repo currently has only `main`.
