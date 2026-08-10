# Starter Project Workflow Progress

Date: 2026-06-07 15:42 +0800

Linear: TAL-296

## Done

- Added the first `paradev new` CLI path for creating a buildable HOI4 starter project from an empty folder.
- Added `Project.create(...)` and `create_project(...)` SDK helpers that write `paradev.yaml`, source/build/output roots, and one starter `modifier` module.
- Covered the starter workflow from both CLI and Python SDK examples.
- Updated the build-flow documentation with copyable CLI and SDK starter commands.

## Verification

- `rtk uv run pytest tests/test_cli.py::test_new_creates_buildable_starter_project` failed before implementation because `new` was not a CLI command.
- `rtk uv run pytest tests/test_cli.py::test_new_creates_buildable_starter_project` passed after implementation.
- `rtk uv run pytest tests/test_sdk_examples.py::test_project_create_build_and_emit_sdk_example` passed.
- `rtk uv run pytest tests/test_cli.py` passed: 7 tests.
- `rtk uv run pytest tests/test_sdk_examples.py` passed: 3 tests.
- `rtk uv run pytest tests/test_project_build.py::test_project_build_returns_dry_run_result_without_writing_by_default tests/test_project_build.py::test_project_build_can_emit_manifest_files_when_requested` passed.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/__init__.py src/paradev/sdk/project.py tests/test_cli.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk uv build` passed and built `dist/paradev-0.1.0.0.dev0.tar.gz` plus `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk bash scripts/test.bash` passed: 328 tests.

## Linear Sync

- Pending final gate run; prior Linear reads failed with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Risks Or Blockers

- Linear sync still needs re-authentication before TAL-296 can be updated.
- The starter workflow creates a minimal buildable modifier project; descriptor and launcher `.mod` preview artifacts remain part of the broader Issue 6 package workflow.

## Next

- Add mod descriptor/launcher metadata artifacts and keep the starter workflow documented from the modder perspective.
