# 2026-06-29 08:41 - HOI4 Game Root Editor LSP

## Slice

- Propagated the SDK-backed `paradev.hoi4.game_root` setting from `configPageSettings` into module editors.
- Passed the configured game root through `ModuleEditor`, `ModuleEntityDetails`, and `SourceCodeEditor` into existing PDX LSP CodeMirror extensions.
- Locked the TypeScript service boundary so Tauri receives `gameRoot` and native-web REST receives `game_root`.
- Extended REST LSP coverage to prove `/lsp/completion` can use a provided HOI4 game root for keyword completions.

## Verification

- Red checks first:
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/SourceCodeEditor.test.tsx src/components/Workspace.moduleEditorConfig.test.tsx src/moduleEditor/ModuleEditor.gameRoot.test.tsx src/moduleEditor/pdxLsp.test.ts`
- Green/final checks:
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/SourceCodeEditor.test.tsx src/components/Workspace.moduleEditorConfig.test.tsx src/moduleEditor/ModuleEditor.gameRoot.test.tsx src/moduleEditor/pdxLsp.test.ts src/services/paradev.test.ts`
  - `rtk uv run pytest tests/test_lsp.py -k "rest_routes or modifiers"`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk npm --prefix apps/desktop run test:unit -- --run`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_lsp.py`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`
  - `rtk git diff --check`

## Tauri Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Verified the native module editor opens PIHC3 Countries and source-code definition tabs still render through CodeMirror after the game-root context wiring.
- Screenshots:
  - `/tmp/paradev-tauri-lsp-game-root-module.png`
  - `/tmp/paradev-tauri-lsp-game-root-source-editor.png`
