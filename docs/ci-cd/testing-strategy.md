# Testing strategy

| Layer | What | Runs in CI |
|---|---|---|
| Unit | Parser, redactor, detector, store with synthetic command lines | Yes |
| Hook | Source the hook in a non-interactive `zsh -i` test and check the log line | Yes |
| Integration | Full pipeline with a fake `claude` binary on `$PATH` | Yes |
| Real | One real `claude -p` call (`pytest -m real`) | No, opt-in locally |
| Prompt quality | Card quality on fixtures (`pytest -m prompt`) | No, opt-in locally |

## Rules
- Fixtures are synthetic. Never commit real history lines ([security/threat-model.md](../security/threat-model.md)).
- The redactor has a dedicated test table of secret-looking lines that must never reach the prompt.
- CI never has access to a Claude token.

**TBD:** Benchmark test for hook latency (fail if the hook takes more than the budget in [requirements/non-functional.md](../requirements/non-functional.md))?
