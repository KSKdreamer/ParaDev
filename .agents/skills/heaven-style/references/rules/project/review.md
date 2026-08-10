---
id: review
title: Review checklist
enabled: true
blocking: true
order: 200
category: project
keywords: [pr gate, code review, style review, inline comments, findings, approval, review criteria]
description: Use for PR, diff, module, branch, or Linear review, severity-marked findings, review artifacts, follow-up, or explicit waivers.
---

# Review checklist

## Core rule

Use this rule for reviews of code changes, recent changes, branches, modules, PRs, or Linear issues. The task playbook is [../../tasks/code-review.md](../../tasks/code-review.md).

Reviews are findings-first, severity-marked, and grounded in file/line evidence whenever possible.

## Apply when

- The task asks for review, PR review, diff review, recent-change review, branch review, module review, or Linear issue review.
- A change needs an explicit completion gate or waiver record.

## Do

- Lead with findings ordered by severity.
- Include file/line references whenever available.
- Re-check the diff before fixing findings because the working tree may change.
- State verification commands and residual risk.

## Avoid

- Leading with a summary before findings.
- Reverting unrelated changes.
- Treating style preferences as bugs without concrete impact.

## Criteria

- **Code quality:** Heaven style, repo conventions, `heavenbase.utils`, config ownership, type hints, naming, and canonical OOP vocabulary.
- **Modularity:** clean boundaries, clear ownership, layering, and extension through registered providers/handlers rather than shortcuts.
- **Brevity:** minimal readable implementation; no avoidable boilerplate, duplicated branches, over-abstracted helpers, or unnecessary files.
- **Ease of use:** straightforward mental model for users and developers; no parallel APIs, confusing flags, or alternate-name-heavy surfaces.
- **Cleanliness:** no ad-hoc hacks, backward-compat leftovers, dead code, debug prints, stale placeholders, or unused artifacts.
- **Docstrings:** user-facing APIs have detailed Google-style docstrings with `Args`, `Returns`, and relevant `Raises`, warnings, or examples.
- **Robustness:** invalid input, security issues, corner cases, swallowed errors, resource leaks, races, and unsafe fallbacks are handled.
- **Migration alignment:** predecessor functionality remains available through the new cleaner API; see [../code/compat.md](../code/compat.md).
- **Sync:** tests, docs, HeavenBase docs, architecture markdown, generated artifacts, examples in the relevant rules, and Linear issue state match the code.

## Severity

- `P0`: blocking correctness, security, data loss, or deployability issue.
- `P1`: likely bug, broken public contract, missing critical validation, or serious test/doc mismatch.
- `P2`: maintainability, modularity, coverage, docstring, or sync issue that should be addressed before declaring done.
- `P3`: polish, naming nuance, optional cleanup, or future improvement.

## Finding Template

```text
- [ ] P1 `config` `test` path/to/file.py:42
  Problem: Model default is hard-coded in a public API and has no error-path test.
  Impact: Downstream projects cannot override it through CM_HVNB and regressions are hard to catch.
  Fix: Route the default through CM_HVNB and add happy/edge/error coverage.
  User annotation:
```

## Output Rules

- Lead with findings, ordered by severity.
- Include file/line references whenever available.
- Assume the working tree may change while you review. Re-check the diff before fixing findings, preserve unrelated external edits, and call out when a finding may have already been addressed by parallel work.
- Save review reports with checkboxes and user annotation fields when the task asks for a durable review.
- For Linear-backed review follow-up, edit one rolling status/review comment for routine updates instead of creating repeated comments.
- State verification commands run and any gaps.
- If no findings exist, say so directly and name residual risk.

## Related rules

Apply all matched code/project rules for the reviewed diff, including [environment.md](environment.md) for verification-command policy. Use [../../tasks/code-review.md](../../tasks/code-review.md) for durable review workflow.
