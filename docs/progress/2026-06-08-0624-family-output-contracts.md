# Family Output Contracts Progress

Date: 2026-06-08 06:24 CST

Linear: TAL-299, TAL-294, TAL-295

## Done

- Added derived `outputs` rows to `Project.families()` and `paradev.build.families_view(...)` so frontend, importer, MCP, and CLI clients can read planned artifact contracts directly.
- Added `index["output_artifact_type"]` for family rows while keeping `index["artifact_type"]` scoped to writer rows.
- Updated `--artifact-type` family filtering to include families that can plan the selected output type, not just registered writers.
- Documented the output contract in the bilingual user manual, developer manual, and build-flow workflow docs.

## Verification

- `rtk bash scripts/test.bash tests/test_build_registry.py tests/test_project.py -k families -q`
- `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_project_build.py::test_project_build_uses_manifest_python_registry_module -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py src/paradev/build/views.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_registry.py tests/test_project.py tests/test_project_build.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`

## Risks Or Blockers

- None in this slice. Future compiler families should rely on declared templates and slots so the derived `outputs` contract remains complete.

## Next

- Continue closing frontend-facing `planned` APIs around module edit flows, PDX/LSP operations, and generic module compilation diagnostics.
