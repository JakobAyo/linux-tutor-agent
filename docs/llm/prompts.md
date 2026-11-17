# Prompts

One prompt per card type ([pedagogy/card-format.md](../pedagogy/card-format.md)). Each prompt contains:

1. The redacted command line I ran ([security/redaction.md](../security/redaction.md)).
2. Grounding: man excerpt, `--help`, tldr, package info ([grounding/local-docs.md](../grounding/local-docs.md)).
3. The instruction to only use flags present in the grounding, and to say so when unsure.
4. Known items from the store, so the card doesn't re-explain what I already understand.

**TBD:** Output format: free Markdown, or structured output (JSON with fields like flags, variations, concept) rendered by the tool? Structured output makes validation possible (e.g. reject flags not found in the man page).

**TBD:** How are prompts tested: fixtures plus an opt-in `pytest -m prompt` suite that makes real calls?
