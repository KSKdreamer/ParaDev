---
id: skill-update
task_kind: skill-update
status: active
enabled: true
order: 40
keywords: [update heaven-style, maintain skill, refresh skill, update rules, update tasks, skill version]
triggers: [skill-update, update heaven-style, stabilize heaven-style, TAL-215, TAL-231]
description: Use when maintaining heaven-style rules, tasks, workflows, scripts, indexes, versions, or failure patterns.
related_rules: [overview, util, config, docs, review, environment, format, test, clean]
---

# Skill Update Task

## Goal

Keep `heaven-style` aligned with the current HeavenBase codebase, docs ecosystem, recurring agent failures, and local history patterns without making normal coding slower.

## Architecture

- `SKILL.md` is the fast path. A small coding or review task should succeed from it plus one directly matched task/failure/rule file.
- `references/tasks/` contains stable active workflows only: `code`, `code-review`, `doc-sync`, `doc-trans`, `test-compress`, `code-explain`, `arch-design`, `manager`, and `skill-update`.
- `references/tasks/arch-design.md` is the task entry point for architecture design and periodic architecture review.
- `references/rules/` contains detailed criteria and focused examples for large refactors, public APIs, shared utilities, storage/query behavior, and tradeoffs.
- `references/workflows/architect.md` is the design-only workflow route: docs organization, module designs, architecture reviews, refactor plans, goals updates, API standard tables, and step-by-step execution plans.
- `references/workflows/developer.md` is the expanded planning/refactor route during implementation.
- `references/workflows/editor.md` is the skill-maintenance route.
- `references/failures/` contains recurring blocker playbooks and subagent delegation prompts.
- `scripts/sync.py` refreshes `assets/heavenbase-reference`.
- `scripts/index.py` regenerates `references/index.yaml` from frontmatter, scripts, assets, and skill metadata.
- `scripts/install.py` is the one-shot updater: run sync, then index, then install the standard global copy at `~/.agents/skills/heaven-style`; `--all-harnesses` also installs the Claude Code plugin bridge without writing `~/.claude/skills/heaven-style`; `--mirror` copies into repos that intentionally embed the skill.
- `scripts/scan.py` checks skill Python scripts for banned stdlib utility imports.

## Repo sync

- Edit heaven-style in **Blueprint** only. Blueprint `.agents/skills/heaven-style/` is canonical.
- After rule/task/script/index changes, run `rtk uv run python .agents/skills/heaven-style/scripts/install.py` from Blueprint for the global install.
- HeavenBase does not track an in-repo skill copy; it uses the standard global install. Use `--mirror <path>` only for repos that intentionally embed a copy.
- Do not edit any embedded in-repo copy directly unless applying an emergency hotfix; backport the same change to Blueprint immediately.

## Update Workflow

1. Read this file, `SKILL.md`, `references/workflows/editor.md`, `references/index.yaml`, and the changed script/task/rule/failure surfaces.
2. Read current HeavenBase evidence before changing rules: `AGENTS.md`, `pyproject.toml`, `src/heavenbase/version.py`, `src/heavenbase/utils/`, config/LLM/DB/MCP/backends/workspace/query/catalog modules, tests, examples, and docs that describe those surfaces.
3. Compare sibling docs and traces when relevant: `HeavenBase-docs`, Mintlify guide files, Cursor/Codex/Copilot/OpenCode histories, and prior review artifacts. Extract repeated requirements, not one-off preferences.
4. Update `SKILL.md` only for daily notices, task routing, and default criteria needed for fast coding. Move detailed or situational guidance into task/rule/failure files.
5. Add or revise a task only when the workflow is stable, repeated, and cannot fit an existing task. Keep tasks non-overlapping.
6. Add or revise failure playbooks when the same blocker pattern appears repeatedly and needs a safe recovery path or subagent handoff.
7. Keep examples grounded in current HeavenBase APIs; for predecessor names, see [compat.md](../rules/code/compat.md).
8. Keep the skill version on `MAJOR.MINOR.PATCH.N[devK]`; the current heaven-style train is `0.1.1`. Bump `N` (and optional `devK`) for skill-only edits; realign with `heavenbase.version.__version__` on HeavenBase-aligned releases.
9. Run `rtk uv run python scripts/install.py` from the Blueprint skill root to refresh the standard global install and `assets/heavenbase-reference/`. Use `--all-harnesses` when Claude Code should consume the generated plugin bridge too. When the skill is embedded in HeavenBase itself, `install.py` skips reference sync automatically; use `~/.agents/skills/heaven-style` for the reference clone. `install.py` must always leave the index current.
10. Run validation and report changed surfaces, evidence sources, version changes, commands, and any waivers.

## Version Criteria

- Schema: `MAJOR.MINOR.PATCH.N[devK]` (for example `0.1.1.2`).
- `MAJOR.MINOR.PATCH` is the release train; heaven-style and HeavenBase share the `0.1.1` train on aligned releases.
- `N` is the very small frequent-updates fourth segment.
- Optional `devK` (`dev0`, `dev1`, …) marks in-development snapshots; omit for stabilized releases.
- The skill may lead HeavenBase between releases; skill frontmatter `version` and `src/heavenbase/version.py` must match on HeavenBase-aligned releases.
- Blueprint and HeavenBase-docs follow the same schema and stay aligned with HeavenBase when version bumps are intentional.

## Verification

From the Blueprint repo root:

```bash
rtk uv run python .agents/skills/heaven-style/scripts/install.py
rtk uv run python .agents/skills/heaven-style/scripts/index.py --check
rtk uv run python .agents/skills/heaven-style/scripts/scan.py .agents/skills/heaven-style/scripts
rtk uv run python -m py_compile .agents/skills/heaven-style/scripts/index.py .agents/skills/heaven-style/scripts/install.py .agents/skills/heaven-style/scripts/sync.py .agents/skills/heaven-style/scripts/scan.py
rtk bash scripts/flake.bash --ci --paths .agents/skills/heaven-style/scripts
```

Also run repo lint/test wrappers through `rtk` + `uv` when script behavior or HeavenBase version code changes; see [../rules/project/environment.md](../rules/project/environment.md).
