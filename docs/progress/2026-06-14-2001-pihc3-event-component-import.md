# 2026-06-14 20:01 CST - PIHC3 Event Component Import

## Done

- Added the `event_component` family with one shared path-preserving PDX slot for reviewed compiled event support files.
- Added `projects/PIHC3/scripts/migrate_pihc2_event_components.py` to import `events/BCE.txt` into one aggregate PIHC3 module.
- Generated `src/modules/event_component/EVENT_COMPONENT_PIHC_BCE_EVENT_SUPPORT/` with `meta.yaml`, copied PDX, and legacy source provenance.
- Excluded `events/BCE.txt` from the PIHC3 copy overlay so the native component owns the compiled output path.
- Updated the event migration docs, copy-overlay posture, design rollup, legacy inventory, and dedicated event-component note.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k event_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_event_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-event-component-build-final.json`

The build reports 16,556 modules across 87 families, 36,216 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest contains 1 `event_component` artifact and 0 copy-root-owned `events/` artifacts.

## Risk

- This slice preserves compiled BCE event support first. It does not yet reconstruct editable border-conflict event authoring from `resources/copies/data/events/BCE.json`.
- Normal event namespaces remain under `event`; compiled event sprites and DDS pictures remain under `event_asset_component`; superevent pairs remain under `superevent`.

## Next

- Continue trimming remaining non-map copy-root buckets, especially train/army support assets, thumbnail handling, and remaining static GFX/entity support that is not map-owned.
