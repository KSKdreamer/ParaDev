# SDK CLI Intro Sections Progress

Date: 2026-06-16 10:25 CST

Linear: N/A

## Done

- Extracted the repeated SDK/CLI reference language intro shape into `_frontend_api_sdk_cli_language_intro_section`.
- Kept the compact SDK/CLI API reference heading, bilingual text, regeneration command, summary, feature summary, and operation matrix unchanged.
- Preserved generated SDK/CLI reference structure and text.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py docs/progress/2026-06-16-1025-sdk-cli-intro-sections.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for this slice; it is intended as a private renderer refactor only.

## Next

- Continue tightening generated API reference renderer helpers while preserving SDK, CLI, REST, MCP, and desktop-facing contracts.
