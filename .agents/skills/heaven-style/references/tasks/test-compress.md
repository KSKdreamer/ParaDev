---
id: test-compress
task_kind: test-compress
status: active
enabled: true
order: 34
keywords: [test compression, compress tests, prune tests, pytest cleanup, legacy tests, fast tests, full tests, test markers, suite cleanup]
triggers: [test-compress, compress tests, prune tests, cleanup tests, reduce tests, slim tests, test suite cleanup]
description: Use when auditing and slimming a pytest suite by removing oddly specific, legacy, low-value, brittle, or redundant tests while preserving meaningful behavior coverage.
related_rules: [overview, test, clean, model, compat, environment, format, docs, review]
---

# Test Compress Task

## Goal

Turn an overgrown pytest suite into a compact, maintainable coverage set that protects public behavior, important bugs, and meaningful edge/error paths without freezing incidental implementation details.

## Fast Path

1. Read repo `AGENTS.md`, [test.md](../rules/project/test.md), `pyproject.toml` pytest marker config, `scripts/test.bash`, and any named issue/plan/report before editing tests.
2. Inventory tests with `rg --files tests` and group them by module, behavior contract, cost, dependency, and marker status.
3. Classify each cluster as keep, merge, retag, rewrite, or drop. Keep behavior-contract tests, durable regression tests, user-facing edge/error coverage, and integration routes that prove a real supported path.
4. Drop or rewrite tests that only assert old internals, migration leftovers, arbitrary fixture details, incidental order/timing, duplicated branches, overly narrow snapshots, generic `test_works` claims, or unsupported legacy behavior.
5. Keep test code modular and generic: share focused fixtures/factories, parametrize equivalent cases, assert observable outcomes, and avoid test names or assertions that describe non-specified behavior.
6. Tag retained tests with `fast` for daily deterministic checks, `full` for expensive merge/release validation, and narrower project markers such as `unit`, `integration`, `slow`, `provider`, or `db` when they clarify runtime cost or external dependencies.
7. Run targeted or fast-marker tests first, then run full-marker or whole-suite validation only when the compression touches broad behavior, public contracts, large PR gates, or release gates.

## Keep Criteria

- Public API contracts, CLI behavior, documented examples, and stable config/resource behavior.
- Regression tests for real bugs that could plausibly recur.
- One representative happy path, edge case, and error path per behavior surface.
- Integration/provider tests that prove supported routes and are tagged by cost/dependency.

## Drop Criteria

- Oddly specific expectations about private helper calls, fixture shape, object identity, timing, ordering, or serialized whitespace when those details are not contractual.
- Legacy compatibility behavior that the current docs, APIs, and release policy no longer support.
- Redundant tests whose meaningful assertion is already covered by a clearer test at the same or higher behavioral level.
- Low-value generated snapshots or broad smoke tests that pass without proving a contract.

## Completion Gate

Do not mark done until the retained suite has clear marker coverage, deleted tests are justified by non-contract or redundant status, targeted fast tests pass, and any skipped full validation is explicitly waived with the reason. For substantial suite compression, save the keep/drop rationale in a plan, progress note, or review/refactor report.

## Verification Commands

```bash
rtk bash scripts/test.bash tests/<target> -q
rtk bash scripts/test.bash -m "fast and not full" -q
rtk bash scripts/test.bash -m full
```

Run `rtk bash scripts/test.bash` only when broad confidence is needed for a large PR merge, release, or sweeping test rewrite.

## Output

Report the number and kind of tests kept, merged, retagged, rewritten, and dropped; the marker policy now supported by the suite; verification commands; and any full-suite waiver.
