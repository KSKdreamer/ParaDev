# PIHC3 AI Component Metadata

Slice: enrich the compiled AI support component importer without adding per-domain module logic.

Changes:

- Added generic AI source metadata to `projects/PIHC3/scripts/migrate_pihc2_ai_components.py`.
- Kept `ai_component` to one shared path-preserving `pdx` slot.
- Regenerated 34 modules under `projects/PIHC3/src/modules/ai_component/`.
- Documented the metadata contract in the AI migration note, design note, and legacy inventory.

Metadata now records component id, source slot/counts, AI source domain, byte/line/nonempty-line counts, top-level block count, ordered top-level keys, bounded first/last top-level key samples, and direct field-key counts inside top-level blocks.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k ai_component` -> 3 passed, 201 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_ai_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_ai_components.py --clean` -> 34 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 34 reviewed `common/ai_*` outputs owned by `module:ai_component/...`.

Remaining work:

- Structured editing for individual AI attitudes, personalities, equipment priorities, country strategies, strategy plans, division templates, and naval templates remains future work.
- Gameplay behavior validation for country AI remains future work.
