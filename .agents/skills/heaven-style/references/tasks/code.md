---
id: code
task_kind: code
status: active
enabled: true
order: 10
keywords: [implement feature, fix bug, modify code, refactor code, add tests, update docs, linear issue, stabilize]
triggers: [implement, fix, code, refactor, add feature, change behavior, stabilize, TAL]
description: Use when implementing Heaven-style features, fixes, refactors, tests, docs, or stabilization work.
related_rules: [overview, util, config, types, oop, model, name, py, clean, error, sql, compat, environment, format, test, docs, extension]
---

# Code Task

## Goal

Ship a small or medium code change in Heaven style without loading the full rule tree unless the change needs it.

## Fast Path

1. Read the user request, repo `AGENTS.md`, the `environment` rule, lint/test wrappers, docs, and nearby source before editing.
2. If a Linear issue, plan file, or previous review is named, read it and extract objective, scope, acceptance criteria, open questions, and status.
3. Brainstorm only when the design is under-specified. Prefer one recommended approach with tradeoffs; then detail the accepted plan.
4. Define the behavior change, public API impact, data/storage impact, docs/example impact, test surface, and non-goals.
5. For small local changes, use `SKILL.md` plus only directly matched rules from `references/rules/overview.md`.
6. For public APIs, shared utilities, storage/query layers, extension points, or cross-module refactors, load `references/workflows/developer.md` and the relevant rules before editing.
7. Apply minimal diffs using existing project patterns. Do not add compatibility shims, leftover aliases, parallel APIs, or temporary wrappers unless explicitly approved.
8. Exercise the feature with a quick probe, smoke path, or demo before broader validation when the behavior is user-facing or integration-heavy.
9. Add or update tests for the happy path, one edge case, and one error path when behavior changes. Add a short demo when the repo requires one.
10. Review the diff against Heaven-style criteria, fix confirmed issues, and repeat targeted tests as needed.
11. Run style scanner, lint/flake/format wrappers, and repo tests through `rtk` + `uv`-backed repo scripts. Use repo wrappers instead of bare tools.
12. Sync user-facing docs, sibling docs repos, architecture docs, generated capability docs, examples, and issue status when the code changes their claims.
13. For Linear-driven work, edit the issue's existing rolling status comment for routine progress, verification, and next steps. Add a new comment only for a distinct decision, blocker, handoff, or user-requested update.

## Coding Criteria

- Code quality: follow Heaven style, repo guidance, `heavenbase.utils` for covered concerns, `CM_HVNB` for shared infrastructure config, and canonical rule IDs.
- Modularity: keep clean OOP boundaries, preserve layering, and extend registry/provider systems through their registration APIs.
- Brevity: prefer the smallest readable implementation; remove boilerplate, redundant helpers, and repeated branches.
- Ease of use: keep public mental models straightforward for users and maintainers; avoid unnecessary classes, modes, flags, or DSL branches.
- Cleanliness: remove ad-hoc code, dead code, stale TODOs, debug prints, compatibility leftovers, and unused artifacts.
- Docstrings: every user-facing public API needs type hints and Google-style docstrings with `Args`, `Returns`, and `Raises` or warning notes/examples when useful.
- Robustness: validate unsupported values, use contextual exceptions, avoid swallowed errors, and cover corner cases.
- Legacy migration: when replacing a predecessor package, follow [compat.md](../rules/code/compat.md) and preserve supported behavior only through the new cleaner API.
- Sync: docs, examples, generated files, architecture notes, sibling docs repos, and Linear issue state must match the implementation when relevant.

## Completion Gate

Do not mark done until the implementation, tests, review, flake/format, docs/example sync, generated artifacts, Linear updates, and final human report are either completed or explicitly waived with the reason.

## Output

Report what changed by rule/category, which verification commands ran, and any risks or explicit waivers.
