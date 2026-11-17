# Supply chain

The repo is public ([ADR 0004](../decisions/0004-public-repo.md)), so the build and dependencies are hardened.

- **Dependabot:** weekly updates for Python dependencies and GitHub Actions.
- **Pinned actions:** third-party actions pinned to a commit SHA.
- **Least privilege:** workflows default to `permissions: contents: read`; write scopes only per job where needed.
- **CodeQL:** code scanning on PRs and a weekly schedule.
- **Secret scanning and push protection:** enabled in repo settings; a pre-commit secret scanner locally (e.g. gitleaks).
- **Lock file:** `uv.lock` committed; CI installs with `--locked`.
- **No secrets in CI:** tests use a fake `claude`; publishing uses OIDC.

**TBD:** Signed commits/tags and build provenance (e.g. GitHub artifact attestations)?
