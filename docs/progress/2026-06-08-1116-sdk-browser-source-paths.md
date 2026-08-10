# SDK Browser Source Path Progress

Date: 2026-06-08 11:16 CST

Linear: TAL-298, TAL-297

## Done

- Fixed `Project.browser()` canonical module source rows so `path` is an absolute project-contained file path and `relative_path` includes the project-relative module path.
- Resolved canonical collection source rows against their loader root when available, keeping collection browser payloads on the same local-reader contract.
- Added browser contract coverage proving canonical scaffolded module sources are readable from the project root.
- Updated the surface architecture contract to specify absolute source `path` plus project-relative `relative_path`.

## Verification

- Red check: `tests/test_project.py::test_project_browser_canonical_sources_are_project_readable` failed first because source rows emitted `path: "def.pdx"`.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_browser_lists_canonical_and_imported_source_families tests/test_project.py::test_project_browser_canonical_sources_are_project_readable tests/test_project.py::test_project_browser_can_filter_one_family tests/test_project.py::test_project_scaffold_module_dry_runs_by_default tests/test_project.py::test_project_create_module_is_intuitive_sdk_alias tests/test_sdk_examples.py::test_pihc3_create_module_uses_family_shorthand -q`: 6 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py tests/test_project.py`: passed.
- `rtk uv run paradev desktop-state --project projects/PIHC3 --json`: PIHC3 idea browser source rows now have absolute file paths and `src/modules/...` relative paths.
- `rtk npm --prefix apps/desktop run test:model`: 8 passed.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- This fixes source loading for read/browser payloads. Text edit apply, removal drafts, and image replacement still need REST/OpenAPI mutation routes.

## Next

- Continue toward REST/OpenAPI apply for source-slot edits, removals, and assets.
