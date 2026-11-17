# Git workflow

`develop` + `main` model ([ADR 0017](../decisions/0017-develop-and-main-branches.md)):

- Feature branches off `develop`. PRs into `develop` are squash-merged, and the PR title must be a Conventional Commit (it drives the version and the CHANGELOG).
- `develop` → `main` with a merge commit. release-please then opens a release PR ([release.md](release.md)).
- Branch protection on `main` and `develop`: required checks, no force push. (Not set up yet.)
- Never edit `CHANGELOG.md` or the version by hand.
