# 0001: Docs structure follows the Single Responsibility Principle

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
Project decisions and design notes need a home that stays easy to navigate as the project grows, both for me and for agents that load the docs as context. The project is a public repo, so CI/CD, security, and community concerns need a place from the start.

## Decision
- `docs/` is split into folders that each answer one question: vision, requirements, observation, detection, grounding, pedagogy, llm, security, ui, architecture, operations, ci-cd, community, milestones, decisions, glossary.
- Each file covers one topic. `docs/CLAUDE.md` is only an index.
- Decisions are recorded as ADRs in `decisions/`. Topic folders describe the current state.
- Undecided points are marked `**TBD:**` with the question to ask, so a later session can find them with `grep -rn TBD docs/` and ask instead of guessing.
- The layout mirrors `../tutor-agent` where the concerns are the same.

## Alternatives considered
- A single design doc (the original `BRAINSTORM.md`): easy to start, hard to navigate and expensive to load as context. Its content was split into the topic files and the file removed.
- Detection and grounding inside `observation/`: mixes capturing, deciding, and fact sourcing, three separate responsibilities.

## Consequences
- More files, but each is small and focused, so an agent loads only what it needs.
- Every new decision means writing an ADR, updating the topic file, and removing its TBD.
