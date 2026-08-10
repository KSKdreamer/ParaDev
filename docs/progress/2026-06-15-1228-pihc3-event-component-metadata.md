# PIHC3 Event Component Metadata

Date: 2026-06-15

## Slice

Expanded the PIHC2 BCE event support importer so `EVENT_COMPONENT_PIHC_BCE_EVENT_SUPPORT` is no longer metadata-thin. The importer still preserves the compiled `events/BCE.txt` file byte-for-byte through the shared path-preserving `pdx` slot, but `meta.yaml` now records the component id, source slot counts, aggregate line/byte totals, 9 `add_namespace` declarations, 9 top-level `country_event` records, 9 options, BCE event ids, option localization keys, the shared picture key, event field-key counts, option field-key counts, and a per-file summary.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k event_component`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_event_components.py tests/test_pihc3_migration_contracts.py`
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-event-component-metadata-build.json`

The build reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest owns `events/BCE.txt` with `module:event_component/EVENT_COMPONENT_PIHC_BCE_EVENT_SUPPORT`, with 0 copy-root-owned artifacts under `events/`.
