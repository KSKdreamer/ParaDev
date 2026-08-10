# Module Draft SDK Ownership

Time: 2026-06-29 21:51 CST

Continued the SDK-first usability loop by moving module draft creation behind a public Python API.

- Added `Project.create_module_draft(...)` so frontend browser family ids such as `ideas` resolve through the SDK before delegating to `Project.scaffold_module(...)`.
- Thinned the REST module draft helper to request decoding plus a call into the SDK method.
- Added the `module.draft` frontend API SDK binding and regenerated Project API, Frontend API, SDK/CLI, API catalog, and desktop TypeScript references.
- Added regression coverage for browser-family resolution and the `module.draft` SDK binding.

Validation:

- `rtk bash scripts/test.bash tests/test_project.py tests/test_tauri_bridge.py -q`: 202 passed.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q`: 242 passed.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py tests/test_api_catalog_selector_helpers.py -q -k "api_catalog or project_api or frontend_api or sdk_cli_reference"`: 70 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/surfaces/rest.py src/paradev/sdk/frontend_api.py src/paradev/sdk/project_api.py tests/test_project.py tests/test_architecture.py tests/test_cli.py`: OK.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.
- `rtk bash scripts/test.bash`: 1199 passed, 1 warning.

Risks:

- The draft payload schema intentionally remains `paradev.rest.module_draft.v1` for compatibility; renaming it to an SDK schema is a separate cross-surface migration.
- This slice did not change PIHC3 content.
