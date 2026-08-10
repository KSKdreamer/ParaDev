---
id: test
title: Tests and examples
enabled: true
blocking: true
order: 110
category: project
keywords: [pytest, unit test, fast test, full test, test marker, runnable example, demo script, coverage, happy path, edge case, error path]
description: Use when adding or reviewing behavior tests, runnable examples, smoke checks, integration evidence, or LLM/provider tests.
---

# Tests and examples

## Core rule

Behavior changes need focused verification through the repository entrypoint. Keep pytest suites intentionally limited and marker-gated: use `fast` for daily agent/developer checks, reserve `full` for large PR merge or release validation, and add narrower project markers such as `unit`, `integration`, `slow`, `provider`, or `db` when they clarify cost or dependency. For new features, cover the happy path, one edge case, and one error path unless explicitly waived.

## Apply when

- Code changes behavior, provider routes, integrations, public APIs, examples, or smoke checks.
- Test coverage, LLM/provider/database/MCP evidence, or no-mock policy is under discussion.

## Do

- Put tests under the workspace test root.
- Start with targeted tests or a smoke probe for touched behavior.
- Tag tests with `fast`/`full` or clearer project categories so agents can run the useful subset instead of the whole suite by default.
- Prefer targeted or fast-marker runs for daily feature sessions; run the full suite only for broad refactors, large PR merge gates, release gates, or when touched behavior needs it.
- Run broader repo wrappers before completion; follow [environment.md](environment.md) for `rtk` + `uv` command policy.
- Keep runnable examples small and route runtime output to the repo's declared temp folder.
- Follow `AGENTS.md` for model, cost, credentials, and no-mock policy.

## Avoid

- Generic `test_works` coverage.
- Oddly specific, legacy, duplicated, or implementation-detail tests that freeze non-contract behavior.
- Running every full, slow, provider, or external-dependency test on every agent feature session when a targeted or fast check covers the changed behavior.
- Documenting provider/backend support before a real route is exercised or explicitly waived.
- Example-generated runtime data outside the declared temp folder.

## Example

```python
def test_works():
    assert run("ok")
```

## Good pattern

```python
def test_run_happy_path(): ...
def test_run_empty_input(): ...
def test_run_unknown_mode_raises(): ...
```

Runnable examples start with an `Objective:` docstring.

## Verification commands

```bash
rtk bash scripts/test.bash tests/test_<area>.py -q
rtk bash scripts/test.bash -m "fast and not full" -q
rtk bash scripts/test.bash -m full
rtk bash scripts/test.bash
```

An empty `tests/` directory is valid when the repo has not added tests yet; the wrapper should exit successfully with a no-tests message.

Use repo wrappers for external-database, LLM, full-marker, or slow-marker suites; read `AGENTS.md` for marker and model policy.

## Related rules

Also apply [environment.md](environment.md) for command wrappers, [format.md](format.md) for lint/format wrappers, [docs.md](docs.md) when examples affect docs, and [review.md](review.md) for completion gates.
