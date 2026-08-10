# Frontend API Index Helper Exports

Date: 2026-06-14 20:55 Asia/Shanghai

## Summary

- Exposed the maintained frontend API index helpers through `paradev.sdk` so Python callers do not need to scan raw contract rows.
- Routed CLI and MCP contract registration through `get_frontend_api_binding_index(...)` instead of unpacking the raw binding index inline.
- Synced SDK/API documentation with the helper-based group, status, mode, surface, payload, workspace section, binding, and index-catalog lookup paths.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py`
- Targeted frontend API helper, CLI contract, MCP contract, SDK CLI reference, and CLI frontend API output tests.
- Direct SDK probe for exported helper imports, CLI/MCP binding-index parity, and representative group/status/mode/surface/payload/workspace-section helper results.

## Notes

- This is a behavior-preserving API-boundary refactor that keeps adapters and docs on the maintained frontend API lookup helpers.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
