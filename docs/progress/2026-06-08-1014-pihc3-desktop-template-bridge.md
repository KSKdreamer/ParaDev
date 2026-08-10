# PIHC3 Desktop Template Bridge Progress

Date: 2026-06-08 10:14

Linear: TAL-297

## Done

- Added SDK authoring templates to the desktop state payload so the GUI receives the same `Project.templates()` contract as CLI and Python callers.
- Wired the template payload from `App` through `AppShell`, `Workspace`, and `ModuleEditor`, including split panes.
- Updated the module editor New action to prefer the unambiguous project-local template for the selected family.
- Template-backed drafts now use the template family and source files, so a PIHC3 idea draft starts as `IDEA_DRAFT_001` with `meta`, `def`, and `loc` source tabs.
- Empty module-family panes now still expose the New action, so the first module in a family is creatable from the GUI draft surface.
- Updated the GUI spec to keep future create forms tied to SDK template metadata and the `advanced` field contract.

## Verification

```bash
npm run test:model
npm run build
rtk bash scripts/test.bash tests/test_cli.py::test_desktop_state_cli_returns_projects_and_browser_payload tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q
rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py tests/test_cli.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_cli.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- Desktop model tests: 4 passed.
- Desktop TypeScript/Vite build: passed.
- Targeted SDK/CLI/template tests: 3 passed.
- Flake: 2 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.

## Risks Or Blockers

- The GUI still uses a one-click local draft placeholder. Actual write/apply behavior remains blocked on the REST/OpenAPI draft mutation path.
- The next GUI slice should render the minimal create form from template args instead of using only the default title.

## Next

- Add a compact create-module form that shows non-advanced template args first and hides defaulted fields by default.
