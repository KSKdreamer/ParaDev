# PIHC3 Copy Overlay Trim Progress

Date: 2026-06-28 18:30

Linear: unlinked

## Done

- Removed stale explicit `object_id` metadata from `projects/PIHC3/src/modules/focus_tree/GENERIC/meta.yaml`; folder identity now stays inferred.
- Added copy-root excludes for already-native BOP, country, individual opinion modifier, special-project project/reward, and `gfx/entities/buildings.gfx` outputs.
- Imported four root static `gfx/entities/` support files into `support_component` modules while keeping the hand-authored `buildings.gfx` startup-compatibility module intact.
- Imported four reviewed `gfx/FX/` shader/include support files into path-preserving `support_component` modules.
- Imported eight reviewed `gfx/models/` border mesh/material support files into path-preserving `support_component` modules.
- Imported the reviewed `gfx/minimap/minimap.dds` file into a path-preserving `support_component` module.
- Imported 28 reviewed `gfx/maparrows/` DDS/config files into path-preserving `support_component` modules.
- Imported 30 reviewed `gfx/particles/` GFX/asset/NUDGE effect files into path-preserving `support_component` modules.
- Imported two reviewed `common/terrain/*.txt` support files into path-preserving `common_component` modules.
- Imported 330 compiled PIHC_dev `map/strategicregions/*.txt` files into native `strategic_region` modules and excluded those paths from the copy root.
- Imported 64 reviewed `map/terrain` BMP/DDS/PNG assets into path-preserving `support_component` modules and excluded those paths from the copy root.
- Imported 29 reviewed root `map/` files into path-preserving `support_component` modules and excluded those exact paths from the copy root.
- Imported 902 compiled PIHC_dev `history/states/*.txt` files into native `state` modules and excluded those paths from the copy root.
- Updated PIHC3 migration notes so the current copy-overlay posture records 0 active diagnostics and 0 remaining compatibility-owned copy-root artifacts.
- Removed ignored local `.DS_Store`, `__pycache__`, and `.pyc` debris from the PIHC3 nested project tree.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'generic_focus_tree_uses_inferred_module_identity or copy_overlay_has_no_native_cutover_shadow_warnings'` failed on the stale metadata and 547 active `copy_root.shadowed_artifact` diagnostics.
- Focused green check: the same command passed with `2 passed, 287 deselected`.
- Support-component red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_static_gfx_entities_without_copy_overlay'` failed before the importer/overlay change, then passed with `3 passed, 287 deselected`.
- `gfx/FX` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_static_gfx_fx_without_copy_overlay'` failed before the importer/overlay change, then passed with `3 passed, 288 deselected`.
- `gfx/models` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_static_gfx_models_without_copy_overlay'` failed before the importer/overlay change, then passed with `3 passed, 289 deselected`.
- `gfx/minimap` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_static_gfx_minimap_without_copy_overlay'` failed before the importer/overlay change, then passed with `3 passed, 290 deselected`.
- `gfx/maparrows` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_static_gfx_maparrows_without_copy_overlay'` failed before the importer/overlay change, then passed with `3 passed, 291 deselected`.
- `gfx/particles` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_static_gfx_particles_without_copy_overlay'` failed before the importer/overlay change, then passed with `3 passed, 292 deselected`.
- `common/terrain` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'common_component_family_preserves_compiled_paths or common_component_importer_extracts_compiled_support_files or common_component_importer_extracts_metadata_contract or common_component_owns_common_terrain_without_copy_overlay'` failed before the importer/overlay change, then passed after the test expectation was aligned with the existing writer's trailing-newline behavior.
- `map/strategicregions` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'strategic_region_family_preserves_compiled_paths or strategic_region_importer_extracts_compiled_regions or strategic_region_importer_extracts_metadata_contract or strategic_regions_are_native_without_copy_overlay'` failed before the importer/overlay change because the importer was missing and the sample paths were still copy-root owned, then passed with `4 passed, 298 deselected`.
- `map/terrain` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_map_terrain_without_copy_overlay'` failed before the importer/overlay change because the support importer still returned 92 files and sampled terrain assets were copy-root owned, then passed with `3 passed, 300 deselected`.
- Root `map/` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'support_component_importer_extracts_misc_compiled_support_files or support_component_importer_extracts_file_metadata_contract or support_component_owns_root_map_files_without_copy_overlay'` failed before the importer/overlay change because the support importer still returned 156 files and sampled root map files were copy-root owned, then passed with `3 passed, 301 deselected`.
- `history/states` red/green check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'state_family_preserves_compiled_paths or state_importer_extracts_compiled_states or state_importer_extracts_metadata_contract or states_are_native_without_copy_overlay'` failed before the importer/overlay change because the state importer was missing and sampled state files were copy-root owned, then passed with `4 passed, 304 deselected`.
- PIHC3 summary after the trim: `rtk bash projects/PIHC3/compile.bash --summary --json` reported 18,003 modules, 78 collections, 37,209 artifacts, 0 diagnostics, 0 errors, and `blocked: false`. This current working-tree count includes five unrelated untracked `PIHC_STATE_TEMPERATURE` modules already present in the nested PIHC3 tree.
- Artifact-owner spot check confirmed representative former shadow paths are now owned only by native module artifacts; the latest owner probe reported `copy_artifacts 0`; `history/states/*` samples owned by `module:state/...`; both `common/terrain/*.txt` files owned by `module:common_component/...`; sample `map/strategicregions/*.txt` files owned by `module:strategic_region/...`; sample `map/terrain/*` and root `map/*` files owned by `module:support_component/...`; and 0 diagnostics.

## Risks Or Blockers

- No `copy_root:pihc_dev` artifacts remain in the current PIHC3 build summary.
- In this local macOS session, running pytest can recreate root `.DS_Store` files under `projects/PIHC3`; final tree hygiene should be checked with `find` after cleanup.

## Next

- Continue higher-level parity review where useful, starting with map/state validation and gameplay balancing rather than copy-overlay ownership.
