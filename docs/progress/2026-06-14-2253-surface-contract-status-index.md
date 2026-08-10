# Surface Contract Status Index Progress

Date: 2026-06-14 22:53

Linear: TAL-299

## Done

- Added `status_index` to `get_surface_contract_summary()` so API tables can group static surface contracts without scanning rows.
- Added `get_surface_contract_status_ids(status)` as the copied-list helper for implemented/scaffold surface slices.
- Updated architecture and developer docs to point table and dashboard code at the SDK-owned status helper.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries -q`
- Direct helper probe for `get_surface_contract_status_ids("scaffold")` and unknown-status error handling.

## Risks Or Blockers

- Full-suite tests intentionally deferred to avoid CPU contention with concurrent PIHC3 migration workers.

## Next

- Continue converting API-table callers to SDK-owned indexes instead of local row scans.
