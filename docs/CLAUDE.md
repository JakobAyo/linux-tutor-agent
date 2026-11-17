# Docs Index

Each folder has one responsibility. Each file covers one topic. Read only the folder you need.

| Folder | Responsibility (answers the question) |
|---|---|
| [vision/](vision/) | **Why** does this project exist, and what counts as success? |
| [requirements/](requirements/) | **What** must the tutor do, and how well? |
| [observation/](observation/) | **How** are commands captured from the shell? |
| [detection/](detection/) | **How** do we decide that something is new to me? |
| [grounding/](grounding/) | **Where** do facts come from, so the LLM can't invent flags? |
| [pedagogy/](pedagogy/) | **How** does the tutor teach and measure learning? |
| [llm/](llm/) | **How** is Claude (`claude -p`) used? |
| [security/](security/) | **How** are secrets and privacy protected? |
| [ui/](ui/) | **How** do I interact with the tutor? |
| [architecture/](architecture/) | **How** is it built (components, data, flow)? |
| [operations/](operations/) | **How** is it installed and run on a machine? |
| [ci-cd/](ci-cd/) | **How** is quality enforced, and how is it released? |
| [community/](community/) | **How** do outsiders use and contribute (public repo)? |
| [milestones/](milestones/) | **When** is what built? Start at [overview](milestones/overview.md). |
| [decisions/](decisions/) | **Which** choices were made, when, and why (ADRs)? |
| [glossary/](glossary/) | **What** do our terms mean? |

## Rules
- Folders describe the **current state**. `decisions/` holds the **history**: why the current state is what it is.
- A new decision goes in a new ADR (`decisions/NNNN-title.md`, from `0000-template.md`). Then update the affected topic file, remove its `TBD`, and link back to the ADR.
- Don't edit an accepted ADR. Supersede it with a new one.
- When a file grows past one topic, split it and update this index.

## Open questions (TBD)
Undecided points are marked `**TBD:**` followed by the question to ask. Find them all with:

```sh
grep -rn "TBD" docs/
```

When starting a session, ask the user about the relevant TBDs before designing or building on them. Do not guess an answer and write it down as decided.
