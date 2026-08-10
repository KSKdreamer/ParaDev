# SDK And CLI API Reference Projection

Date: 2026-06-08 20:56 CST

Issues: TAL-299, TAL-295

Linear comments: TAL-299 `8883a4c3-4d00-4074-a3c0-a8a567542163`, TAL-295 `bbceb682-ff14-4eab-b30f-5bd92171a61a`

## Summary

This slice adds a compact generated SDK/CLI API matrix for HoI4 modders, automation scripts, and agents that need the simplest answer to "which Python SDK call or CLI command should I use?" The full frontend API reference already covered SDK, CLI, REST, MCP, LSP, payload, and input details, but it was intentionally dense for GUI and adapter developers. The new page is generated from the same canonical frontend API contract and lists operation id, group, read/write mode, Python SDK call, CLI command, inputs, and summary.

The generated page lives at `docs/user-manual/sdk-cli-reference.md` and is produced by:

```bash
rtk uv run paradev frontend-api --sdk-cli-markdown > docs/user-manual/sdk-cli-reference.md
```

## Changes

- Added `render_frontend_api_sdk_cli_markdown()` to the public SDK export.
- Added CLI projection `paradev frontend-api --sdk-cli-markdown`.
- Added `sdk-cli-markdown` to the static CLI surface contract projection list.
- Added generated `docs/user-manual/sdk-cli-reference.md`.
- Linked the new page from the user manual index, Python SDK manual, frontend API manual, and developer manual.
- Added architecture coverage that keeps the generated SDK/CLI reference byte-for-byte aligned with the SDK renderer.
- Added CLI coverage for the new projection and conflict behavior.

## User Impact

HoI4 mod developers now have a shorter manual path for day-to-day use:

- Use `docs/user-manual/sdk-python.md` for examples.
- Use `docs/user-manual/sdk-cli-reference.md` for the generated API matrix.
- Use `docs/user-manual/frontend-api-reference.md` only when REST, MCP, LSP, payload, or binding details are needed.

This keeps the user-facing mental model smaller while preserving the single SDK-owned operation list for GUI and adapter developers.

## Verification

- `rtk python -m py_compile src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 88 passed, 3 skipped because optional `fastapi.testclient` is unavailable in the default environment.
- `rtk npm --prefix apps/desktop run test:unit` -> 31 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py` -> passed.
- `rtk bash scripts/flake.bash --ci` -> passed.
- `rtk git diff --check` -> passed.
- CLI probe: `rtk uv run paradev frontend-api --sdk-cli-markdown` rendered the generated matrix with 75 operations, 74 implemented rows, and one frontend-local row.

## Review Notes

- This is a documentation/projection slice; it does not add or remove canonical frontend API operations.
- PIHC3/TAL-297 remains out of scope for this shared SDK/manual work.
- The known `.bash_profile` `autoload`/`compinit` warnings still appear when running commands through `rtk bash -lc`, but the generation commands exited successfully.
