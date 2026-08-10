---
id: environment
title: Agent environment and commands
enabled: true
blocking: true
order: 95
category: project
keywords: [rtk, uv, AGENTS.md, scripts/_env.bash, bash wrapper, python path, venv, sync-env.bash, sync wrapper, command prefix, coding agent]
description: Use when running shell commands, choosing Python/uv executables, adding Bash wrappers, or diagnosing wrong-environment failures for coding agents.
---

# Agent environment and commands

## Core rule

Read repo `AGENTS.md` first. Heaven-lineage repos are `uv`-first: run work through repo Bash wrappers that source `scripts/_env.bash`. When the session provides `rtk`, prefix the **entire** agent shell command with it. For Python in uv-first repos, that normally means repo wrappers or `rtk uv run python`, not `rtk python`; bare PATH Python can resolve to broken system or Conda shims. Do not bypass wrappers with bare `python`, `pytest`, `black`, `flake8`, or ad-hoc `pip install` when the repo declares `scripts/*.bash`.

Dependency source of truth: **`requirements*.txt`**, with `pyproject.toml` referencing those files. Install priority when setup is unavoidable outside wrappers: **uv → pip (`requirements*.txt`) → pyproject (`pip install -e ".[dev]"`) → conda (`environment-*.yml`) → poetry (`poetry.lock`)**.

## Apply when

- Starting implementation, verification, release, sync, lint, test, benchmark, or docs-generation work.
- Adding or reviewing repo Bash wrappers or CI command examples.
- A coding agent chooses shell commands, Python executables, or environment setup steps.
- Commands fail with missing modules, wrong interpreter, or `uv` not found.

## Do

- Read `AGENTS.md` for repo-specific wrapper names, extras, markers, demo paths, and release policy.
- Prefix the full agent shell command with `rtk` when available (`rtk bash ...`, `rtk uv ...`, `rtk uv run python ...`).
- For ad-hoc repo Python probes, use `rtk uv run python ...` or a Bash wrapper helper. Use `rtk python ...` only when deliberately testing PATH/system Python behavior.
- Prefer repo wrappers in this order when they exist (wrapper name comes from repo `AGENTS.md`; Blueprint and HeavenBase use `scripts/sync-env.bash`):
  1. `rtk bash scripts/sync-env.bash`
  2. `rtk bash scripts/flake.bash --ci` or `-a`
  3. `rtk bash scripts/test.bash`
  4. repo-specific wrappers such as `release.bash`, `benchmark.bash`, or `sync-readme.bash`
- Use direct `uv` only when no wrapper exists or the wrapper explicitly forwards extra args, for example `rtk uv build` or `rtk uv run <tool>`.
- Source `scripts/_env.bash` in new Bash wrappers and call `resolve_uv`, `run_python`, or `run_uv_python` instead of duplicating interpreter lookup.
- Honor repo Python preference env vars when hooks or CI need `uv` first: `REPO_PYTHON_PREFERENCE`, `HEAVENBASE_PYTHON_PREFERENCE`, or `BLUEPRINT_PYTHON_PREFERENCE` set to `uv-first`.
- Report the exact wrapper, `uv` path, and Python resolution used when env failures block progress.

## Avoid

- Bare `pytest`, `black`, `flake8`, `python -m pytest`, `rtk python ...`, or `pip install -e .` when repo wrappers or `uv run` are the intended repo environment.
- Conda activation or hand-maintained `requirements*.txt` as the primary setup path in `uv`-first repos.
- Hard-coded `python`/`uv` lookup ladders copied into every Bash script.
- Assuming `rtk` replaces repo wrappers; `rtk` wraps the outer command, it does not replace `bash scripts/test.bash`.
- Treating heaven-style skill-maintenance scripts as target-repo commands.

## Command ladder

```text
AGENTS.md
  -> rtk (when session provides it)
    -> bash scripts/<wrapper>.bash
      -> scripts/_env.bash
        -> uv / uv.exe
          -> repo .venv or uv-managed env
```

## `_env.bash` contract

Shared helpers in `scripts/_env.bash`:

- `resolve_uv` / `resolve_uv_optional` — prefer `uv` before `uv.exe`
- `resolve_python` / `run_python` — active venv, repo `.venv`, `uv run python`, then system Python
- `run_uv_python` — force `uv run python`

New repo wrappers should set `ROOT`, `cd` to it, `source "${ROOT}/scripts/_env.bash"`, then call helpers.

## Exceptions

- **Skill maintenance:** scripts under `.agents/skills/heaven-style/scripts/` may use bare `python` from a known-good shell; prefer `rtk uv run python` in agent sessions.
- **CI:** GitHub Actions may call `uv sync` and `bash scripts/...` directly without `rtk`.
- **Non-uv legacy repos:** follow that repo's `AGENTS.md`; do not force `uv` where the repo is not `uv`-first.

## Example

```bash
pytest tests -q
python -m black src
pip install -e ".[dev]"
```

## Good pattern

```bash
rtk bash scripts/sync-env.bash
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash tests/test_config_manager.py -q
rtk uv build
```

HeavenBase also uses `scripts/sync-env.bash` and commonly adds:

```bash
rtk bash scripts/benchmark.bash
rtk bash scripts/release.bash
```

## Related rules

Also apply [format.md](format.md) for lint/format wrapper details, [test.md](test.md) for pytest markers and evidence policy, and [../../failures/env.md](../../failures/env.md) when commands still fail after the wrapper ladder is used.
