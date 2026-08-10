# ParaDev Workflows

Status: active guide

Date: 2026-06-06

Purpose: keep `AGENTS.md` short while giving agents concrete operating workflows.

## Feature Work

1. Start from a Linear issue in the `Talirian` workspace, `ParaDev` project. If no issue exists, create one from [../goals/short-term-plan.md](../goals/short-term-plan.md).
2. Read [../README.md](../README.md), then follow the reading path for the task type.
3. Check current code and docs before changing files. Prefer `rg` and existing repo APIs.
4. Define the smallest testable slice and state acceptance criteria in the issue or local plan.
5. Implement through the Python SDK first; CLI, MCP, REST, desktop, and editor surfaces should call SDK contracts.
6. Update docs, demos, and Linear when behavior or public workflow changes.

## Five-Hour Checkpoint

Run this checkpoint at least every five active work hours, and before stopping a long task.

1. Capture status:

```bash
rtk git status --short
rtk git diff --stat
```

2. Run Heaven style on changed Python paths:

```bash
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src tests
```

Use narrower paths when only a few Python files changed.

3. Run targeted tests for the changed area, then the standard gates when feasible:

```bash
rtk bash scripts/test.bash tests/test_target.py -q
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
```

The standard no-argument test gate is the parallel fast suite and excludes tests marked `slow`. Run `rtk bash scripts/test.bash --full` before release or migration sign-off when the PIHC3 parity contracts need to be included.

4. Review the diff for correctness, missing tests, stale docs, generated files, and unrelated changes.
5. Write a progress note under [../progress/](../progress/).
6. Update the Linear issue with progress, verification, blockers, and next step.
7. Commit and push only if the slice is coherent and verification is documented.

## Build Flow

Use [build-flow.md](build-flow.md) for the current user-facing SDK and CLI build path. It covers dry runs, artifact emission, dependency/source-map manifests, profile overrides, and the minimal demo project.

## CLI Output

Use `--json` whenever another tool consumes command output. JSON mode emits valid JSON for mappings, lists, and scalar values such as `paradev cfg get paradev.project.name --json`; omit it for human-readable YAML or plain scalar text.

## Testing

- Unit and integration tests:

```bash
rtk bash scripts/test.bash
rtk bash scripts/test.bash --parallel
rtk bash scripts/test.bash --full --parallel
rtk bash scripts/test.bash --slow --parallel
rtk bash scripts/test.bash --serial
rtk bash scripts/test.bash tests/test_pdx_roundtrip.py -q
```

`scripts/test.bash` defaults to the parallel fast suite when no pytest arguments are supplied. `--full` preserves the all-tests behavior, `--slow` runs only marked slow contracts such as the PIHC3 migration parity checks, and `--serial` disables the default xdist run for order-sensitive debugging.

- Lint and formatting check:

```bash
rtk bash scripts/flake.bash --ci
```

- Apply Black plus Flake8 when intentionally formatting:

```bash
rtk bash scripts/flake.bash --all
```

- Package build:

```bash
rtk uv build
```

## Desktop App

- Desktop TypeScript unit checks for helper/data contracts:

```bash
rtk npm --prefix apps/desktop run test:unit
```

- Fast frontend check:

```bash
rtk bash scripts/run.bash --web
```

- Build-time browser preview with the native REST bridge:

```bash
rtk bash scripts/run.bash --native-web
```

- Installed host without opening a window:

```bash
rtk uv run paradev dashboard --no-open
```

- Reproducible Python application build and macOS lifecycle smoke:

```bash
rtk bash scripts/build-wheel.bash
rtk bash scripts/smoke-macos-installed-app.bash \
  --wheel dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl
```

For visible UI changes, inspect the running app with the in-app browser or a desktop test workflow and verify desktop and mobile-width layouts when relevant. Keep HOI4 business logic out of React components.

## Packaging

1. Sync dependencies after `pyproject.toml` changes:

```bash
rtk bash scripts/sync-env.bash
```

2. Build the Python wheel with the exact packaged React/Vite output and host assets:

```bash
rtk bash scripts/build-wheel.bash
```

3. When desktop behavior changes on macOS, smoke the installed Finder/Dock app:

```bash
rtk bash scripts/smoke-macos-installed-app.bash \
  --wheel dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl
```

4. Record generated wheel paths and verification in the Linear issue or progress note. Windows native packaging remains deferred.

## Git And GitHub

Target remote:

```bash
git remote add origin git@github.com:PIHC-Team/ParaDev.git
```

Use this only if `origin` is missing. The default branch is `master`.

Before committing:

```bash
rtk git status --short
rtk git diff --stat
```

Commit and push:

```bash
rtk git add <intentional paths>
rtk git commit -m "<scope>: <summary>"
rtk git push -u origin master
```

Do not stage unrelated dirty files. If another user or agent changed a file, preserve their work and mention the overlap in the progress note.
