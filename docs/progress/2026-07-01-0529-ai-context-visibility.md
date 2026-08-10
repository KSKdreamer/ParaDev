# 2026-07-01 05:29 - AI chat context visibility

## Summary

Verified the current ParaDev environment is already on `heavenbase==0.1.1.5` and continued the floating AI chat usability pass. The SDK-owned create-module and build chat prompts now name the Python API calls they should guide users toward, and the floating chat shows the exact attached context state before a message is sent.

## Changes

- Anchored the create-module role prompt to `Project.templates()` and `Project.create_module_draft(...)`.
- Anchored the build role prompt to `Project.build(...)` and `desktop_project_build_command(...)`.
- Added a visible floating-chat context summary such as `Context: Workspace state, Templates (8)` or `No context attached`.
- Styled selected context chips in both the floating chat and Config Models page so attached sources are visually distinct.
- Added English and Chinese translations plus component, locale, service, and Python contract coverage.

## Verification

- `rtk uv run python -c "import heavenbase, paradev; print('heavenbase', heavenbase.__version__); print('paradev', paradev.__version__)"`
- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_ai_chat_profile_catalog tests/test_desktop_api_selection.py::test_desktop_ai_chat_includes_metadata_source_content -q`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts src/services/paradev.test.ts`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/sync-env.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47841`

## Notes

The PIHC3 Tauri smoke reached `target/debug/paradev-desktop` with no terminal-side startup errors and was stopped after a short idle window. The next SDK-first AI chat slice should add visible operation cards for chat profiles that map to generated frontend API operations such as `module.draft` and `build.start`, without parsing LLM prose or auto-running writes.
