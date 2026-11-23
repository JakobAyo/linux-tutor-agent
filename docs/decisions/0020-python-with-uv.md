# 0020: Python with uv as the core language

- **Status:** Accepted
- **Date:** 2026-11-23

## Context
[architecture/tech-stack.md](../architecture/tech-stack.md) left open whether the core is Python 3.12+ with uv or a language with a single static binary (Go, Rust). The spike is Python (stdlib only), and the reader is going to be a Textual TUI ([ADR 0021](0021-textual-tui-reader.md)), which is a Python library.

## Decision
The core is Python 3.12+, managed with uv (`pyproject.toml`, `uv.lock`). During development it is installed system-wide with `uv tool install --editable .`.

## Alternatives considered
- Go or Rust: a single static binary is nicer for an AUR package, but rules out Textual and means rewriting the spike's logic.

## Consequences
- The spike's code can be ported instead of rewritten.
- How it's distributed (PyPI, AUR, …) is still open ([operations/installation.md](../operations/installation.md)).
- Updated: [architecture/tech-stack.md](../architecture/tech-stack.md), [architecture/components.md](../architecture/components.md).
