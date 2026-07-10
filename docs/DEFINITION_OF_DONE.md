# Definition of Done

No milestone or major feature in BugHunter is considered complete until it satisfies the following criteria.

## Checklist

- [ ] **Code implemented**: Feature logic is complete.
- [ ] **Tests added**: Dedicated unit or integration tests exist for the new logic.
- [ ] **Existing tests pass**: No regressions (`pytest` passes 100%).
- [ ] **Documentation updated**: README, user guides, or API references reflect the change.
- [ ] **ADR updated**: If the architecture changed, an Architecture Decision Record was added/updated.
- [ ] **Doctor passes**: `bughunter doctor` verifies the environment remains healthy.
- [ ] **No lint/type errors**: Ruff, Black, and Mypy checks pass.
- [ ] **No TODOs left in production code**: Unfinished thoughts are tracked in `docs/TECH_DEBT.md`.
- [ ] **Release checklist updated**: Validation gates for the specific phase are verified.
