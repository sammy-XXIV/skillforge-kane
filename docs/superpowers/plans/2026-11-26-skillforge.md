# SkillForge Implementation Plan

**Goal:** Create, verify, repair and reuse real browser-task agent skills.
**Architecture:** Frozen contracts, quarantined procedures, isolated Chrome,
Kane action/analyzer phases, hash-bound evidence, fail-closed registry.
**Tech stack:** Python 3.11+ stdlib, HTML/CSS/JS fixture, Chrome, Kane CLI 0.10.9.
**Spec:** ../specs/2026-11-26-skillforge.md
**Execution:** Inline, authorized autonomously by the user. Fresh review at end.

## Global constraints

- No production fake verifier and no claim of live Kane success from fixtures.
- No execution of generated arbitrary scripts; no shell interpolation.
- All conditions explicitly true, exit codes zero, stream v1 complete.
- Freeze criteria before authoring; repairs modify procedures only.
- Fresh re-verification on reuse; failed or tampered skills leave discovery.

## Review focus

- Incomplete/contradictory Kane output cannot admit a skill.
- Tampered procedures or contracts invalidate previous evidence.
- Variable injection cannot create objective instructions or shell commands.
- Failure on reuse revokes eligibility before returning.
- Concurrency, timeouts and interruptions cannot leave a verified stale skill.

## Task 1: Registry and contracts

Create `skillforge/core.py` and `tests/test_core.py`. Write failing tests for
contract immutability, traversal, candidate quarantine, pass/fail transitions,
hash invalidation and retry bounds. Run `python -m unittest discover -s tests -v`,
expect missing implementation, implement and rerun to green.
Produces Store.create/author/find/verify/run/repair and atomic state writes.

## Task 2: Kane execution

Create `skillforge/kane.py` and `tests/test_kane.py`. Consumes frozen contract
and objective; produces normalized verdict plus raw stdout/stderr for both phases.
Test a real child-process fixture for NDJSON parsing, refusal, timeout, malformed
streams, analyzer false/missing verdicts and argument safety before implementation.
Launch private Chrome with a temp profile; invoke Kane with --agent, --headless,
--cdp-endpoint, --timeout. Analyze the same page separately with --analyzer-only.

## Task 3: Agent surface and demo

Create `skillforge/cli.py`, `forge.py`, package metadata, generator SKILL.md,
trusted wrapper, example contract/procedures, disposable order desk and CI.
Test CLI lifecycle using explicitly labeled fixture subprocesses in tests only;
test real demo flows with Playwright on Linux. Document fresh-session reuse,
repair based on failure evidence, installation, isolation and exact limitations.

## Task 4: Publish and verify

Run complete tests, compile Python, inspect diff and scan for credentials.
Create public `sammy-XXIV/skillforge-kane`; push and run Linux CI. Independently
review the full branch, fix material findings with regression tests. Attempt real
Kane runs when credentials/runtime permit. Preserve truthful verification status.
