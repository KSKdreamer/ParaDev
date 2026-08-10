---
id: failure-env
title: Environment and PATH failures
enabled: true
order: 10
keywords: [wrong python, uv, command not found, PATH, module not found, system error, venv]
description: Use when commands fail because the wrong shell, Python, uv environment, or PATH is active.
---

# Environment and PATH Failures

Load [../rules/project/environment.md](../rules/project/environment.md) first for the normal `rtk` + `uv` + repo-wrapper command ladder.

## Pattern

Commands fail with `program not found`, `ModuleNotFoundError`, wrong Python path, missing packages, broken `python.bat`, or repo wrappers using the wrong environment.

## Response

1. Verify the required repo environment from `AGENTS.md` before blaming code. Heaven-lineage repos are normally `uv`-first, not ad-hoc Conda envs.
2. Prefer repo wrappers over bare tools: `rtk bash scripts/sync-env.bash` (or the sync wrapper named in `AGENTS.md`), `rtk bash scripts/test.bash`, `rtk bash scripts/flake.bash --ci`.
3. Inspect active executables when wrappers still fail: `rtk where uv`, `rtk where python`, `rtk where python3` (or `rtk cmd /c where python` on Windows), and repo `.venv` presence.
4. Run the smallest environment check through the repo wrapper ladder:

```bash
rtk bash scripts/sync-env.bash --check
rtk uv run python -c "import heavenbase; print('ok')"
```

5. If `rtk python` fails but `rtk uv run python` works, treat it as PATH/system-Python drift rather than a repo failure. Keep using wrappers or `rtk uv run python` for repo work.
6. If shell activation fails, call the repo helper path instead of changing global PATH. Bash wrappers source `scripts/_env.bash` and resolve Python as: active virtualenv, repo `.venv`, `uv run python` or `uv.exe run python`, then system Python.
7. If many commands are blocked by env drift, spawn a narrow subagent when available: "diagnose env/PATH only; report exact executable paths and the minimal command prefix to use."
8. Retry the original command only after the environment is proven.

## Do Not

- Do not treat missing dependencies as code regressions until the intended environment is confirmed.
- Do not bypass repo wrappers with bare `pytest`, `black`, `flake8`, or `python -m ...` when wrappers exist.
- Do not edit global shell profiles unless the user explicitly asks.
- Do not hide the chosen interpreter or `uv` path in the final report.
