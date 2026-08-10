# 2026-07-01 08:20 - Desktop config rows API

## Summary

Confirmed ParaDev is already consuming HeavenBase 0.1.1.5: `requirements.txt`,
`uv.lock`, and the embedded Heaven-style skill all point at 0.1.1.5. The
remaining adaptation was SDK-bedrock cleanup rather than a dependency bump.

Added `paradev.desktop.desktop_config_rows()` as the public Python facade for
desktop `CM_PARADEV` config metadata. The TypeScript contract renderer now uses
that API instead of directly serializing the private row constant, so GUI config
controls still get the same keys/defaults/choices but through a formal SDK
surface. Regenerated the desktop API reference and API catalog reference, and
documented the parity rule in `docs/architecture/interfaces.md`.

## Verification

- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/desktop/__init__.py src/paradev/desktop/api.py tests/test_desktop_api_selection.py tests/test_architecture.py`
- `rtk bash scripts/sync-env.bash --check`
- `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade -q`
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages tests/test_api_table_contracts.py::test_api_catalog_rows_match_source_helper_metadata tests/test_api_table_contracts.py::test_api_catalog_lists_every_generated_api_table_helper -q`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python - <<'PY' ...` reported HeavenBase `0.1.1.5`, 14 desktop config rows, and available `LLM`/`Prompt` symbols.
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47850` reached Vite ready, finished Cargo build, launched `target/debug/paradev-desktop`, and showed no late startup output before manual stop.
