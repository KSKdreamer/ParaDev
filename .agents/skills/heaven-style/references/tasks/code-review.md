---
id: code-review
task_kind: code-review
status: active
enabled: true
order: 20
keywords: [review code, review pr, review branch, review recent changes, style review, quality review, linear review]
triggers: [review, code review, check this pr, review TAL, review branch, review changes]
description: Use when reviewing code changes, modules, branches, PRs, recent diffs, or Linear-linked review work.
related_rules: [overview, review, util, config, types, oop, model, name, py, clean, error, sql, compat, environment, format, test, docs, extension]
---

# Code Review Task

## Goal

Systematically review code changes, recent changes, a module, a branch, or a Linear issue against Heaven-style quality criteria.

## Scope Discovery

1. Determine the review target: user-provided files, current diff, recent commits, branch diff, PR, module, or Linear issue.
2. If no target is provided, default to current uncommitted and staged changes.
3. Establish the comparison base explicitly in the report: requested base, merge base, current branch, commit range, or file list.
4. Read repo guidance, nearby source, relevant docs, and the matched rules before judging code.
5. Assume parallel human or agent work may be happening. Re-read `git status` and the target diff before each fix pass, treat unexpected edits as external changes, and do not revert them unless explicitly approved.

## Review Criteria

- Code quality: strictly follow Heaven style, naming, utility/config rules, and local repo conventions.
- Modularity: prefer OOP code with clean ownership, stable boundaries, and registry/extension paths instead of planner or business-logic shortcuts.
- Brevity: code should be as small as the behavior allows; flag boilerplate, duplicate logic, over-abstracted helpers, and unnecessary branches.
- Ease of use: the mental model should be direct for users and developers without heavy cognitive burden.
- Cleanliness: no ad-hoc hacks, backward-compatibility leftovers, dead code, stale placeholders, debug prints, or unused artifacts.
- Docstrings: user-facing APIs need detailed Google-style docstrings with `Args`, `Returns`, and relevant `Raises`, warnings, or examples.
- Robustness: look for vulnerabilities, invalid input paths, corner cases, swallowed exceptions, resource leaks, race conditions, and unsafe fallbacks.
- Migration alignment: if the change replaces a predecessor package, follow [compat.md](../rules/code/compat.md) and verify supported behavior remains available through the new API.
- Sync: docs, HeavenBase docs, architecture markdown, generated artifacts, tests, examples in the relevant rules, and Linear issue state should match the codebase.

## Findings Format

Use findings-first review. Each finding should include:

- Checkbox for triage.
- Severity: `P0` blocking correctness/security/data-loss, `P1` likely bug or broken contract, `P2` maintainability/test/doc gap, `P3` polish or optional cleanup.
- Rule IDs or criteria category.
- File and line reference when available.
- Problem, impact, and concrete fix direction.
- Optional `User annotation:` field for confirming whether the issue is true and urgent.

If there are no findings, say so directly and list any residual review gaps such as tests not run or unavailable context.

For architecture health reviews not anchored to a concrete diff, branch, PR, or module change, route to [arch-design.md](arch-design.md).

## Review Artifact

Save a durable report to `docs/reports/reviews/<YYYY-MM-DD>-<scope>-heaven-style-review.md` when the user asks for a saved review, the task is a Linear/PR gate, or follow-up work needs an auditable artifact. For quick or explicitly read-only reviews, return the findings inline instead. When saving, include:

- Scope and comparison base.
- Commands and evidence inspected.
- Findings with checkboxes and user annotation fields.
- Verification gaps.
- Acceptance criteria for addressing confirmed findings.

Create or update a Linear issue when available and appropriate. The issue criteria should be objective: all confirmed `P0`/`P1` findings are fixed, agreed `P2` findings are handled or waived, relevant tests/docs/examples/generated docs pass, and the review artifact is updated.

For continuous Linear follow-up, edit one rolling review/status comment instead of adding routine progress comments. Add a separate comment only for a distinct decision, blocker, handoff, or explicit user-requested update.

## Default Next Step

After saving and summarizing the report, wait for human annotation before fixing. Proceed directly to fixes only when the user explicitly asks for review-and-fix or gives permission to continue.
