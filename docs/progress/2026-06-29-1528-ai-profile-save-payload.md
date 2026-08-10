# 2026-06-29 15:28 - AI Profile Save Payload

## Slice

Kept editable AI chat profiles from accidentally persisting translated or
unchanged built-in label/detail text as overrides.

## Changes

- Changed `aiChatProfileSaveDraft(...)` so it sends only fields that differ from
  the SDK-provided profile defaults.
- Preserved custom label/detail edits, prompt edits, and source-kind edits.
- Added regression coverage for translated defaults and prompt-only profile
  edits.

## Verification

- Red check before the fix:
  `rtk npm --prefix apps/desktop test -- src/aiChatProfileText.test.ts`
  failed because unchanged built-in label/detail values were still included in
  the save payload.
- `rtk npm --prefix apps/desktop test -- src/aiChatProfileText.test.ts`
- `rtk npm --prefix apps/desktop test -- src/aiChatProfileText.test.ts src/configPage/ConfigPage.test.tsx src/App.test.ts src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop test`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/run.bash --tauri --port 5211`
- Captured native PIHC3 Tauri smoke screenshot:
  `/tmp/paradev-tauri-ai-profile-save.png`.
- `rtk git diff --check`

## Notes

- A read-only subagent found a separate native-web route-alignment issue: some
  services still call bespoke `/desktop/...` bridge routes where canonical
  frontend API REST planning exists. The smallest next slice is likely
  `renameModule(...)` native-web route planning.
- PIHC3 remained clean during this slice.
