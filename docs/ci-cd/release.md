# Release

- **Versioning:** SemVer, starting at `0.x` while in design and spike phases.
- **Automation:** release-please reads Conventional Commits, bumps the version, writes `CHANGELOG.md`, tags, and creates a GitHub release.
- **Publishing:** from the tag, via trusted publishing (OIDC), no long-lived tokens in repo secrets.

**TBD:** Release targets: PyPI, AUR package (`PKGBUILD`, fits an Arch-only tool), GitHub release artifacts, or a combination? Who maintains the AUR package and is its update automated?

**TBD:** When is the first public release (after which milestone)?
