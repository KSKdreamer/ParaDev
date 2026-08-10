# 2026-06-30 04:02 - AI chat dirty source context

## Summary

- Threaded selected module editor draft text into the floating AI chat source descriptor as `sourceContent`.
- Included source-content changes in the module selection target key/equality so chat context refreshes when only editor text changes.
- Preserved intentionally empty editor drafts instead of falling back to saved disk content.
- Tightened the SDK chat source parser so an explicit empty `content` field is treated as live source content, not as a missing field.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/App.test.ts
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_ai_chat_includes_project_source_context tests/test_desktop_api_selection.py::test_desktop_ai_chat_prefers_inline_project_source_content tests/test_desktop_api_selection.py::test_desktop_ai_chat_preserves_empty_inline_project_source_content tests/test_desktop_api_selection.py::test_desktop_ai_chat_includes_metadata_source_content -q
rtk npm --prefix apps/desktop run test:unit
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py
rtk git diff --check
rtk npm --prefix apps/desktop run build
rtk bash scripts/flake.bash --ci
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The frontend tests failed before implementation because selected source descriptors carried only `sourcePath`, not live dirty text.
- The empty-content backend test failed before implementation because the SDK fell back to saved file text.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` and produced no extra runtime output during the smoke window.
- The desktop build still reports the existing Vite large-chunk warning.
