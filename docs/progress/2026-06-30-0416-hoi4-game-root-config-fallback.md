# 2026-06-30 04:16 - HOI4 game root config fallback

## Summary

- Routed HOI4 keyword dataset and completion helpers through `paradev.hoi4.game_root` when callers omit an explicit game root.
- Kept CLI and REST LSP commands as thin SDK wrappers while inheriting the configured root for keyword and completion requests.
- Hardened the LSP server so blank initialization path options are treated as omitted instead of resolving to the current directory.
- Documented the config fallback on the SDK completion API.

## Verification

```bash
rtk bash scripts/test.bash --serial tests/test_hoi4_keywords.py::test_hoi4_keyword_dataset_uses_configured_game_root_when_omitted tests/test_lsp.py::test_lsp_completion_uses_configured_game_root_when_omitted tests/test_lsp.py::test_lsp_rest_keywords_use_configured_game_root_when_query_omitted tests/test_cli.py::test_lsp_keywords_cli_uses_configured_game_root_when_omitted -q
rtk bash scripts/test.bash --serial tests/test_lsp.py::test_pdx_lsp_server_blank_game_root_option_keeps_configured_fallback -q
rtk bash scripts/test.bash --serial tests/test_hoi4_keywords.py tests/test_lsp.py -q
rtk bash scripts/test.bash --serial tests/test_cli.py -k "lsp" -q
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/keywords.py src/paradev/lsp/server.py src/paradev/sdk/lsp.py tests/test_hoi4_keywords.py tests/test_lsp.py tests/test_cli.py
rtk git diff --check
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The first fallback tests failed before implementation because the SDK returned the local Steam install path instead of the configured test root.
- The blank LSP initialization test failed before implementation because `gameRoot: ""` became `Path(".")`.
- The standard fast gate passed with `1218 passed, 1 warning`.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` successfully.
