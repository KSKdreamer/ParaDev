---
name: heaven-style
description: Heaven-style code and architecture guide for Python-first repos in the HeavenBase lineage. Use when writing, reviewing, designing architecture, refactoring, or aligning tests/docs for downstream packages, HeavenBase maintenance, or shared infrastructure code; enforce HeavenBase utilities over stdlib, CM_HVNB config for shared infrastructure, modern type annotations, canonical OOP vocabulary, short names, raise_mismatch, SQL/resource discipline, architecture-review artifacts, code-review artifacts, and repo lint/test gates.
metadata:
  version: 0.1.1.5
---

# Heaven Style

## Default Use

Use Heaven Style when coding, reviewing, refactoring, or aligning docs/tests in HeavenBase-lineage Python projects. Reading this file is enough for normal coding tasks. Load rule files only when the change touches public APIs, shared utilities, storage/query behavior, extension points, broad refactors, or an unclear tradeoff.

HeavenBase is the shared infrastructure foundation: prefer `heavenbase` for public examples, `heavenbase.utils` for utilities/logging/serialization/shell/path helpers, and `CM_HVNB` for shared infrastructure config.

Repo-specific `AGENTS.md` wins for environment, command wrappers, test model policy, demo paths, and release discipline. For shell commands, load [references/rules/project/environment.md](references/rules/project/environment.md).

## Design Philosophy

These principles outrank local repo conventions when they conflict:

- **Minimal mental model.** Expose the shortest OOP-style front door: classmethods create or load objects, instance methods perform lifecycle actions, and common flows read as `obj = Class(...); obj.verb()`. Avoid constructor side-effect flags, nested free-function pipelines, hidden magic, and clever metaprogramming. An average engineer or agent should reconstruct the architecture from one page.
- **Registries over branches.** New backends, providers, handlers, types, and strategies plug in through registration APIs; never extend by editing central planners, routing tables, or `if provider ==` chains.
- **Shared infrastructure first.** `heavenbase.utils` replaces stdlib for covered concerns; `CM_HVNB` owns every tunable. Missing broadly useful helpers go into the shared layer, not local wrappers.
- **Break and fix, no shims.** Renames and redesigns update all call sites in the same change; permanent compatibility layers and parallel `v1/v2` APIs are banned unless explicitly waived.
- **Compact, explicit Python.** Guard clauses, comprehensions, canonical OOP verbs, short hot-path names, contextual errors via `raise_mismatch`; loud failures over silent fallbacks.
- **Docs are part of the code.** Architecture pages, generated artifacts, and examples must match the implementation; a durable mental-model doc beats rediscovering design in chat history.

## Task Surface

- [references/tasks/code.md](references/tasks/code.md): implementation, bug fix, feature, refactor, tests, docs.
- [references/tasks/code-review.md](references/tasks/code-review.md): diff, PR, branch, module, recent changes, or Linear-issue review.
- [references/tasks/doc-sync.md](references/tasks/doc-sync.md): sync English HeavenBase docs, Mintlify pages, navigation, and sibling docs repos.
- [references/tasks/doc-trans.md](references/tasks/doc-trans.md): line-aligned Chinese (`zh/`) MDX translation when explicitly requested.
- [references/tasks/test-compress.md](references/tasks/test-compress.md): audit and compress pytest suites by pruning low-value tests, preserving behavioral contracts, and tagging fast/full coverage.
- [references/tasks/code-explain.md](references/tasks/code-explain.md): explain architecture, data flow, modules, feature behavior, or code-change comparisons for newcomers.
- [references/tasks/arch-design.md](references/tasks/arch-design.md): architecture design, periodic architecture review, module boundaries, dependency health, and agile design plans.
- [references/tasks/manager.md](references/tasks/manager.md): track GitHub and Linear status, stale work, recent work, and next-step orchestration.
- [references/tasks/skill-update.md](references/tasks/skill-update.md): update this skill from HeavenBase codebase changes, scripts, local history, and docs traces.

Keep task playbooks inside this skill by default. Separate wrapper skills such as `heaven-code` or `heaven-review` are useful only as thin discoverability aliases; they should link here and must not duplicate rule text.

## Normal Coding Loop

1. Inspect `AGENTS.md`, the `environment` rule, Linear context if provided, lint/test wrappers, config patterns, docs, and nearby source before editing.
2. Brainstorm only when requirements or design are uncertain: present the best option plus tradeoffs, then detail the plan once accepted.
3. Plan small slices with success criteria, touched APIs, storage/query impact, docs/example impact, tests, and explicit non-goals.
4. For Linear-driven work, read or create the issue, record acceptance criteria, and keep status aligned with the code. For continuous issues, edit one rolling status comment instead of adding routine progress comments.
5. Implement minimal diffs using existing project style and HeavenBase shared utilities.
6. Exercise the behavior with a small probe or demo when useful, then run targeted tests through repo wrappers.
7. Review the diff against the criteria below, fix confirmed issues, and repeat test/review until no blocking findings remain.
8. Run flake/format through repo wrappers, sync docs/examples/generated artifacts/Linear, then report changes, verification, risks, and waivers.

## Coding Criteria

- **Code quality:** use `heavenbase as hb` in public examples, import utility helpers from `heavenbase.utils`, route shared infrastructure config through `CM_HVNB`, and follow local repo style.
- **Modularity:** keep OOP boundaries clean; extend backends/providers/handlers through registry APIs; avoid planner or business-logic shortcuts.
- **Brevity:** prefer compact readable Python, guard clauses, comprehensions, and direct data flow; remove boilerplate, duplicate logic, and unnecessary wrappers.
- **Ease of use:** keep the user/developer mental model obvious; prefer owning-object methods over free-function front doors, and avoid parallel APIs, constructor side-effect flags, unnecessary classes, or alternate-name-heavy methods.
- **Cleanliness:** no ad-hoc hacks, debug prints, dead code, stale placeholders, deprecated aliases, or backward-compatibility shims unless explicitly waived.
- **Docstrings:** public user-facing APIs need type hints and Google-style docstrings with `Args`, `Returns`, and relevant `Raises`, warnings, or examples.
- **Robustness:** validate unsupported values with contextual errors, use `raise_mismatch` where the repo provides it, avoid swallowed exceptions, and cover edge/error paths.
- **Sync:** tests, examples, docs, architecture markdown, generated artifacts, sibling docs repos, and Linear issue state must match the code when relevant.

## Daily Notices

- Use `heavenbase.utils` for covered paths, files, serialization, shell, hash, logging, IDs, and common helpers. If the utility is missing and broadly useful, add it there instead of creating local wrappers.
- Use `CM_HVNB` for HeavenBase-owned defaults: models, providers, gateways, dimensions, batch sizes, timeouts, paths, prompt text, backend presets, and benchmark knobs.
- Keep public APIs small: `heavenbase as hb` in examples, shortest OOP-style flows, canonical OOP verbs, type hints, Google-style docstrings, and one obvious way to do each task.
- For providers/backends/handlers, register capabilities instead of editing central planners or routing tables.
- For docs, verify facts against code, write in friendly professional prose, use realistic code demos, and run Mintlify checks when the docs repo supports them.
- For reviews, assume parallel human/agent work may be happening. Re-read the current diff before judging or fixing, and never revert changes you did not make without explicit approval.
- Versioning uses `MAJOR.MINOR.PATCH.N[devK]` (for example `0.1.1.2`). The current heaven-style train is `0.1.1`; bump `N` for skill-only edits and optional `devK` for in-development snapshots. The skill may lead HeavenBase between releases; align skill `metadata.version` with `heavenbase.version.__version__` on HeavenBase-aligned releases.
- Predecessor names (`pyheaven`, `heaven`, `AgentHeaven`) are legacy; see [references/rules/code/compat.md](references/rules/code/compat.md).

## Rule Map

Use [references/rules/overview.md](references/rules/overview.md) to choose files. Common IDs:

- Code rules: `util`, `config`, `types`, `oop`, `model`, `name`, `py`, `clean`, `error`, `sql`, `compat`.
- Project rules: `environment`, `format`, `test`, `docs`, `review`, `extension`.

Load [references/tasks/arch-design.md](references/tasks/arch-design.md) for architecture design, periodic architecture review, module boundaries, refactor plans, goals updates, API standard tables, and step-by-step execution plans before implementation; it routes to [references/workflows/architect.md](references/workflows/architect.md). Load [references/workflows/developer.md](references/workflows/developer.md) for large refactors, public API design, shared utility work, or rule tradeoffs while coding. Load [references/workflows/editor.md](references/workflows/editor.md) only when maintaining this skill.

## Common Gotos

- Config/default/provider issue: [references/rules/code/config.md](references/rules/code/config.md).
- Stdlib/path/file/serialization/shell/logging issue: [references/rules/code/util.md](references/rules/code/util.md).
- Public API or mental-model issue: [references/rules/code/model.md](references/rules/code/model.md) and [references/rules/code/oop.md](references/rules/code/oop.md).
- Shell commands, `rtk`, `uv`, or wrapper policy: [references/rules/project/environment.md](references/rules/project/environment.md).
- Tests/examples/integration issue: [references/rules/project/test.md](references/rules/project/test.md).
- Docs/Mintlify/sibling-doc sync: [references/tasks/doc-sync.md](references/tasks/doc-sync.md).
- Chinese doc translation: [references/tasks/doc-trans.md](references/tasks/doc-trans.md).
- Architecture/module explanation: [references/tasks/code-explain.md](references/tasks/code-explain.md).
- Architecture design, periodic review, refactor plans, goals, and execution plans: [references/tasks/arch-design.md](references/tasks/arch-design.md).
- HeavenBase architecture work: read `docs/resources/architecture/mental-model.md` in the HeavenBase repo before changing cross-module interfaces.
- Project status and orchestration: [references/tasks/manager.md](references/tasks/manager.md).
- Skill maintenance and version alignment: [references/tasks/skill-update.md](references/tasks/skill-update.md).
- Environment, proxy, auth, or Linear pressure failures: [references/failures/env.md](references/failures/env.md), [references/failures/network-proxy.md](references/failures/network-proxy.md), [references/failures/auth-secrets.md](references/failures/auth-secrets.md), [references/failures/linear-pressure.md](references/failures/linear-pressure.md).

## Verification

Follow [references/rules/project/environment.md](references/rules/project/environment.md). Prefix **every** agent shell command with `rtk` when the session provides it. For repo Python work, prefer repo wrappers or `rtk uv run python`; reserve `rtk python` for deliberate PATH/system-Python diagnostics.

An empty `tests/` directory is valid for template repos such as Blueprint; `rtk bash scripts/test.bash` should report no tests found and exit successfully.

```bash
rtk uv run python .agents/skills/heaven-style/scripts/scan.py <paths>
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
```

When `uv` is unavailable in a known-good skill-maintenance shell, bare `python .agents/skills/heaven-style/scripts/scan.py <paths>` from the repo root is acceptable.

## Review Route

For review requests, load [references/tasks/code-review.md](references/tasks/code-review.md). Reviews are findings-first and severity-marked; save `docs/reports/reviews/` artifacts only for durable Linear/PR gates or when the user asks, and normally wait for human annotation before fixes unless the user asks to proceed.
