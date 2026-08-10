# Config SDK Facade

Time: 2026-06-29 22:22 CST

Continued the SDK-first usability loop by moving the remaining config command helpers behind ParaDev-owned Python APIs.

- Added public `paradev.config` helpers for get, list, set, unset, scopes, and history operations backed by `CM_PARADEV`.
- Routed CLI config commands through those helpers instead of importing HeavenBase config command helpers directly.
- Bound the frontend `project.config` operation to `CM_PARADEV` and regenerated the frontend/API catalog references and desktop TypeScript contract.
- Added config facade round-trip coverage plus API, CLI, and frontend contract assertions for the new SDK row.
- Fixed desktop AI route tests so persisted local `paradev.ai.base_url` values do not make key-env tests environment-dependent.

Validation:

- `rtk bash scripts/test.bash tests/test_config_api_selection.py tests/test_architecture.py tests/test_cli.py -q -k "config_api or frontend_api_contract_lists_canonical_operations or cli_api_table_lists_command_contract or frontend_api_cli_outputs"`: 21 passed.
- `rtk bash scripts/test.bash tests/test_config_api_selection.py tests/test_architecture.py tests/test_cli.py tests/test_api_catalog_selector_helpers.py -q -k "config_api or api_catalog or frontend_api or cli_api_table_lists_command_contract"`: 76 passed.
- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q`: 45 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/config_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/sdk/frontend_api.py tests/test_config_api_selection.py tests/test_architecture.py tests/test_cli.py tests/test_desktop_api_selection.py`: OK.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.
- `rtk bash scripts/test.bash`: 1200 passed, 2 warnings.

Risks:

- `project.config` is now SDK-bound for contract visibility, but the GUI config page still needs a project-aware picker as a separate usability slice.
- This slice did not change PIHC3 content.
