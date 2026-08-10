# Family Authoring Contract Progress

Date: 2026-06-07 17:45

Linear: TAL-295

## Done

- Continued in isolated branch `codex/scaffold-source-root-selection` to avoid the main checkout's parallel PIHC3 and GUI work.
- Added a top-level `authoring` contract to `Project.families()` and `paradev families` with valid source roots plus `modules/{family}/{object_id}` and `collections/{family}/{collection_id}` folder templates.
- Updated English and Chinese user/developer manuals so HoI4 mod authors, GUI agents, MCP tools, importers, and project-local family authors can use SDK-owned layout rules instead of hard-coding discovery paths.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_cli_outputs_profile_family_contracts -q` failed with `KeyError: 'authoring'`.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_cli_outputs_profile_family_contracts tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project.py::test_project_families_exposes_shared_source_slot_contracts tests/test_project.py::test_project_families_exposes_sprite_slot_contracts tests/test_project.py::test_project_families_exposes_collection_source_slot_contracts tests/test_project.py::test_project_families_returns_asset_contracts -q` (`7 passed`)
- CLI smoke: `rtk uv run paradev families demos/assets/projects/minimal --json` returned `authoring.source_roots`, `module_path_template`, and `collection_path_template`.
- Docs grep: `rtk rg -n "Project\\.families|families\\]|authoring|modules/\\{family\\}|collections/\\{family\\}" docs/user-manual docs/workflows/build-flow.md`
- Formatting: `rtk uv run black src/paradev/sdk/project.py tests/test_project.py` (`2 files left unchanged`)
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py` (`OK: 2 file(s) - no banned imports`)
- Diff whitespace: `rtk git diff --check` (clean)
- Lint: `rtk bash scripts/flake.bash --ci` (`48 files would be left unchanged`)
- Full tests: `rtk bash scripts/test.bash` (`341 passed in 68.34s`)
- Package build: `rtk uv build` (`dist/paradev-0.1.0.0.dev0.tar.gz`, `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`)

## Risks Or Blockers

- Linear fetch for `TAL-295` still fails with `UNAUTHORIZED; Session expired`, so this note is the durable sync artifact until auth is refreshed.

## Next

- Continue stabilizing the generic family/build contracts around project-local families and module creation flows that PIHC3 importers and GUI surfaces will call.
