# PIHC3 Scripted Localisation Component Progress

Date: 2026-06-14 17:36 CST

Linear: none

## Done

- Added the `scripted_localisation_component` simple-source family with one path-preserving PDX slot.
- Added `migrate_pihc2_scripted_localisation_components.py` for the 29 reviewed compiled `common/scripted_localisation` support files.
- Imported inventory selector, superevent label, topbar resource, trade/operation helper, and shared state-lore button support files into `src/modules/scripted_localisation_component/`.
- Excluded reviewed scripted-localisation support paths from the PIHC_dev copy overlay while keeping `PIHC_STATE_LORES.txt` owned by the existing state-lore aggregate path.
- Updated migration docs and central legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k scripted_localisation_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_scripted_localisation_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-scripted-localisation-component-build.json`
- Build summary: 16,542 modules, 62 collections, 36,216 artifacts, 1,857 warnings, 0 errors, `blocked: false`.
- Ownership check: all 29 reviewed scripted-localisation support paths are `scripted_localisation_component` owned, with 0 copy-owned and 0 missing.

## Risks Or Blockers

- The slice preserves compiled `defined_text` files path-by-path; it does not create editable `defined_text` record schemas.
- Higher-level inventory selector, superevent label, topbar resource, and state-lore button authoring remain future reconstruction work.

## Next

- Continue with another non-map copy-owned domain such as topbar/interface support, music/audio support, remaining GUI fragments, or other common support roots.
