---
id: workflow-editor
title: Editor workflow
enabled: true
audience: editor
keywords: [maintain heaven-style, edit skill, install skill, update rules, update tasks, update failures, update skill version]
description: Use when maintaining this heaven-style skill, changing rules/tasks/failures/workflows, regenerating indexes, syncing reference assets, or aligning versions.
---

# Editor Workflow

## When to use

Use this surface only when maintaining the `heaven-style` skill itself: editing `SKILL.md`, rules, workflows, task playbooks, failure playbooks, scripts, assets, generated index metadata, or packaged artifacts.

## Skill maintenance workflow

1. Edit the smallest relevant surface:
   - `SKILL.md` for the default fast coding path, task routing, and high-level criteria.
   - `references/tasks/code.md` for implementation workflow details.
   - `references/tasks/code-review.md` for review workflow, artifact, and Linear follow-up details.
   - `references/tasks/doc-sync.md` for docs/Mintlify/sibling-doc workflow details.
   - `references/tasks/doc-trans.md` for line-aligned Chinese MDX translation workflow details.
   - `references/tasks/test-compress.md` for pytest suite compression, marker policy, and low-value test pruning.
   - `references/tasks/code-explain.md` for newcomer-oriented explanation workflow details.
   - `references/tasks/arch-design.md` for architecture design and periodic architecture review workflow details.
   - `references/tasks/manager.md` for GitHub/Linear status and orchestration workflow details.
   - `references/tasks/skill-update.md` for skill architecture, script contracts, and version alignment.
   - `references/failures/` for recurring blocker triage and subagent delegation playbooks.
   - `references/workflows/architect.md` for doc organization, module designs, refactor plans, goals updates, API standard tables, and pre-implementation execution plans.
   - `references/workflows/developer.md` for large refactors, public API design, and full-rule reading during implementation.
   - `references/workflows/editor.md` for skill maintenance.
   - `references/rules/` for rule-selection, code/project rules, and focused good/anti examples.
2. Keep `references/tasks/` minimal. Default active tasks are `code.md`, `code-review.md`, `doc-sync.md`, `doc-trans.md`, `test-compress.md`, `code-explain.md`, `arch-design.md`, `manager.md`, and `skill-update.md`; add another task only for a stable, repeated workflow that cannot fit them.
3. Use trigger-oriented YAML frontmatter. Use `description` and `keywords` for discovery; the Markdown body is normative.
4. Keep examples inside their owning rule and list cross-checks in `Related rules`.
5. Run `rtk uv run python scripts/install.py` from the Blueprint skill root after reference or script changes to refresh the standard global install at `~/.agents/skills/heaven-style`. Use `rtk uv run python scripts/install.py --all-harnesses` when local Claude Code support should be refreshed too; it installs a Claude plugin bridge and does not write `~/.claude/skills/heaven-style`. Skill-maintenance scripts under `.agents/skills/heaven-style/scripts/` may use bare `python` only from a known-good shell; prefer `rtk uv run python` in agent sessions. Target-repo work must still use `AGENTS.md` wrappers, `uv`, and `rtk` when available. When maintaining an embedded in-repo copy, use `rtk uv run python scripts/install.py --skip-sync` (or rely on the embedded auto-skip) and refresh the global install for reference assets.
6. Run `rtk uv run python scripts/index.py --check` after install to confirm generated metadata is current.
7. HeavenBase does not track an in-repo skill copy; it consumes the standard global install. Use `rtk uv run python scripts/install.py --mirror <path> --skip-global` only for repos that intentionally embed a copy.

## Commands

From `.agents/skills/heaven-style/`:

```bash
rtk uv run python scripts/install.py
rtk uv run python scripts/install.py --skip-sync
rtk uv run python scripts/sync.py
rtk uv run python scripts/index.py
rtk uv run python scripts/index.py --check
rtk uv run python scripts/scan.py scripts
```

From the Blueprint repo root after skill edits:

```bash
rtk uv run python .agents/skills/heaven-style/scripts/install.py
rtk uv run python .agents/skills/heaven-style/scripts/install.py --mirror <embedded-skill-path> --skip-global
```

## Self-compliance

The skill must follow its own code-quality rules:

- Scripts use HeavenBase utilities where feasible.
- Scripts pass `scripts/scan.py`.
- Scripts pass repo `flake.bash --ci` (includes `.agents/skills/heaven-style/scripts`) and `py_compile`.
- Skill scripts use one-line docstrings; full Google-style docstrings apply to library public APIs.
- `index.yaml` is generated, not hand-edited.
- Task playbooks are few, active, and non-overlapping.
- Failure playbooks are operational, narrow, and safe around secrets and local machine state.
- Skill version follows `MAJOR.MINOR.PATCH.N[devK]` on the current heaven-style train (`0.1.1`); frontmatter `version` matches `src/heavenbase/version.py` on HeavenBase-aligned releases.

## Install behavior

- `install.py` runs `sync.py`, then `index.py`, so a normal install leaves reference assets and `references/index.yaml` current. Use `--skip-sync` when avoiding network/reference refresh.
- The standard user install path is `~/.agents/skills/heaven-style`; legacy `heaven-style-<version>` installs are removed only after their `SKILL.md` verifies that they are the same skill.
- `--all-harnesses` installs the common Agent Skill plus a Claude Code plugin bridge. It never writes `~/.claude/skills/heaven-style`; use `--backup-claude-skill` only when an existing verified plain Claude skill must be moved aside to avoid duplicate discovery in Cursor, OpenCode, and Kilo.
- When embedded in the HeavenBase repository, `install.py` skips reference sync automatically to avoid a maintenance loop; use `~/.agents/skills/heaven-style` for `assets/heavenbase-reference/`.
- `sync.py` refreshes `assets/heavenbase-reference` in global or sibling skill checkouts only.
- `index.py` indexes rules, workflows, tasks, failures, scripts, and assets.
- `scan.py` checks banned stdlib imports for covered utility concerns.
