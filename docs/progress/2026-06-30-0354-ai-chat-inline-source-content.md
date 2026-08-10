# 2026-06-30 03:54 - AI chat inline source content

## Summary

- Fixed SDK desktop chat source handling so path-backed sources validate project containment but prefer supplied inline `content` over rereading disk.
- Preserved exact inline draft text, including trailing newlines, for prompt context and returned source metadata.
- Kept ordinary saved-file sources on the previous compact payload shape: path, relative path, content length, and truncation state without echoing file content.

## Verification

```bash
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_ai_chat_prefers_inline_project_source_content -q
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_ai_chat_includes_project_source_context tests/test_desktop_api_selection.py::test_desktop_ai_chat_prefers_inline_project_source_content tests/test_desktop_api_selection.py::test_desktop_ai_chat_includes_metadata_source_content tests/test_desktop_api_selection.py::test_desktop_ai_chat_rejects_sources_outside_project -q
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py
rtk git diff --check
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q
rtk bash scripts/flake.bash --ci
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The regression test failed before implementation because the prompt used the old saved file text instead of the supplied draft text.
- Frontend selection targets currently carry only `entityId`, `familyId`, and `sourcePath`; a later GUI slice should thread dirty editor draft text into chat source descriptors.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` and produced no extra runtime output during the smoke window.
