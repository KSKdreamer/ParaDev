# Bundle Surface SDK Ownership

Date: 2026-06-14 21:10 Asia/Shanghai

## Summary

- Added the explicit `sdk_owned` marker to the bundle surface contract.
- Added focused architecture coverage for bundle identifier, scaffold status, tools, outputs, platform priority, and SDK ownership.
- Kept the bundle packaging plan behavior unchanged while making its static contract shape consistent with CLI, MCP, LSP, and VS Code surface contracts.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/bundle.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/bundle.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/bundle.py tests/test_architecture.py`
- Targeted architecture tests for surface coverage and the bundle surface contract.
- Direct SDK probe for `get_bundle_contract()["sdk_owned"]`.

## Notes

- This is a behavior-preserving interface contract alignment for the desktop backend packaging surface.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration and frontend API desktop work continue in parallel.
