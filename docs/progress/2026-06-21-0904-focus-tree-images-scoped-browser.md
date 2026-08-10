# 2026-06-21 09:04 - Focus Tree Images and Scoped Browser Loading

## Summary

- Confirmed PIHC3 focus tree icons are migrated as browser-decodable preview PNGs under `projects/PIHC3/src/modules/focus_asset_component/*/preview.png`; current checkout has 739 preview files.
- Kept desktop startup from blocking on a full project browser by adding `desktop-state --no-browser` and Tauri `includeBrowser: false` support.
- Added a scoped `paradev_project_browser` Tauri command plus TypeScript `loadProjectBrowser(...)`, then wired the app to request only the active module or diagram family on tab open.
- Mapped GUI `focuses` diagram tabs to SDK `focus_tree` requests so PIHC3 focus-tree modules load correctly instead of the empty generic focus family.
- Browser QA on `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html` opened the National Focuses diagram and verified 9/9 focus nodes render actual SVG `<image>` elements with 34 px PNG thumbnails inside 48 px grid cells, with no placeholders.

## Verification

- `rtk uv run pytest tests/test_project.py::test_desktop_state_can_skip_active_browser_payload tests/test_project.py::test_project_cli_desktop_state_can_skip_active_browser_payload`
- `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts src/App.test.ts`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml desktop_state_command_can_skip_browser_payload`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml project_browser_command_loads_scoped_payload`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_focus_tree_preview_icons_resolve_to_migrated_components tests/test_pihc3_migration_contracts.py::test_pihc3_focus_asset_component_importer_groups_focus_sprites_and_icons`
- `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts src/App.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk uv run pytest tests/test_project.py tests/test_pihc3_migration_contracts.py::test_pihc3_focus_tree_preview_icons_resolve_to_migrated_components`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/discovery.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- `rtk npm --prefix apps/desktop run build`

## Notes

- A combined Cargo filter command was rejected because `cargo test` accepts one test filter; the two Rust tests passed when run separately.
- Vite still warns that a few chunks exceed 500 kB after minification. This is pre-existing bundle-size pressure and did not block the build.
