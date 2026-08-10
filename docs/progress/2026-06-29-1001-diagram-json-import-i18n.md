# Diagram JSON Import I18n

## Slice

- Localized diagram JSON parser and import compatibility failures for GUI imports while preserving the SDK-style default English errors when no translator is supplied.
- Wired the module editor diagram import action to pass the active UI translator into the import helper.
- Added regression coverage for a malformed JSON parse failure and a missing ParaDev payload compatibility failure in Chinese.

## Native PIHC3 Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Opened the PIHC3 technology diagram in Chinese and verified the rendered graph was not blank, with technology icons, relationship lines, toolbar controls, and the inspector visible.
- Verified the localized JSON import/export toolbar controls and the JSON editor panel controls through macOS accessibility.
- Tried to submit malformed JSON through the offscreen JSON panel; direct accessibility value setting did not expose the localized error text, so exact error-message behavior is covered by the focused unit regression instead.

Screenshots kept outside the repo:

- `/tmp/paradev-tauri-json-i18n-tech-diagram.png`
- `/tmp/paradev-tauri-json-i18n-toolbar-import.png`

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/diagramEditor/diagramJsonImport.test.ts` first failed before implementation on the expected English parse error.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk git diff --check`
- `rtk git -C projects/PIHC3 status --short --untracked-files=all`
