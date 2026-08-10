# Authoring Path Plans Progress

Date: 2026-06-07 17:55

Linear: TAL-295

## Done

- Continued in isolated branch `codex/scaffold-source-root-selection` to avoid the main checkout's parallel PIHC3 and GUI work.
- Added read-only SDK path planning through `Project.authoring_path(kind, family, target_id, source_root=...)`.
- Added `paradev authoring-path` as a thin CLI wrapper for scripts, GUI adapters, importers, and future MCP tools that need one concrete module or collection root before writing files.
- Updated English and Chinese manuals plus the build-flow contract to distinguish `families`, `authoring-path`, `templates`, and `scaffold`.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_authoring_path_resolves_module_and_collection_roots tests/test_cli.py::test_authoring_path_cli_resolves_configured_source_root -q` failed because `Project.authoring_path(...)` and `paradev authoring-path` were missing.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_authoring_path_resolves_module_and_collection_roots tests/test_cli.py::test_authoring_path_cli_resolves_configured_source_root tests/test_project.py::test_project_scaffold_module_can_select_source_root tests/test_cli.py::test_scaffold_cli_can_select_source_root -q` (`4 passed`)
- CLI smoke: `rtk uv run paradev authoring-path demos/assets/projects/minimal module idea GER_industry_spirit --json`
- Docs grep: `rtk rg -n "authoring-path|Project\\.authoring_path|paradev\\.sdk\\.authoring_path|families\\(\\)\\[\\\"authoring\\\"\\]" docs/user-manual docs/workflows/build-flow.md`
- Formatting: `rtk uv run black src/paradev/cli.py src/paradev/sdk/project.py tests/test_cli.py tests/test_project.py` (`4 files left unchanged`)
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py tests/test_cli.py tests/test_project.py` (`OK: 4 file(s) - no banned imports`)
- Diff whitespace: `rtk git diff --check` (clean)
- Lint: `rtk bash scripts/flake.bash --ci` (`48 files would be left unchanged`)
- Full tests: `rtk bash scripts/test.bash` (`343 passed in 68.94s`)
- Package build: `rtk uv build` (`dist/paradev-0.1.0.0.dev0.tar.gz`, `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`)

## Risks Or Blockers

- Linear fetch for `TAL-295` still fails with `UNAUTHORIZED; Session expired`, so this note is the durable sync artifact until auth is refreshed.

## Next

- Continue tightening generic authoring and build inspection payloads used by PIHC3 importers and GUI surfaces, with project-local family flows as the next likely seam.
