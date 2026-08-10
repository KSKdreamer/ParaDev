# Family Metadata Contract Progress

Date: 2026-06-08 08:39 CST

Linear: TAL-295, TAL-299

## Done

- Extended `Project.families()` / `paradev.build.families_view(...)` metadata rows with `common_keys`, `family_keys`, and `unknown_key_policy` while preserving the existing accepted `keys` list and `settings` contract.
- Updated family contract tests for registry views, SDK project views, and manifest-declared simple, collection, and routed families.
- Updated English/Chinese user and developer docs so GUI, importer, MCP, and REST clients can render metadata forms from the SDK-owned family contract instead of duplicating `meta.yaml` allowlists.

## Verification

- Red-first focused tests failed on missing metadata contract fields.
- `rtk uv run pytest tests/test_build_registry.py::test_families_view_wraps_registry_contract_with_authoring_paths tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family -q`
- `rtk uv run pytest tests/test_build_registry.py tests/test_project.py -k families tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family -q`
- `rtk uv run paradev families demos/assets/projects/minimal --family idea --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_build_registry.py tests/test_project.py tests/test_project_build.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

## Risks Or Blockers

- The metadata contract now explains accepted top-level keys and unknown-key severity. Rich per-key value types, defaults, and descriptions are still future work for family-owned metadata.

## Next

- Continue generic compiler hardening by adding more frontend-ready family contracts for metadata/settings field descriptions or by exposing build graph node details useful to GUI and importer panels.
