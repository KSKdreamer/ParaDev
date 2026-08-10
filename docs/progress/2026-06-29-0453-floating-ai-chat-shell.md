# Floating AI Chat Shell

Time: 2026-06-29 04:53 CST

Continued the AI feature loop by mounting the first global desktop chat UI on top of the existing SDK-owned chat bridge.

- Added a fixed `FloatingChatShell` with closed launcher, open transcript panel, project/route summary, localized copy, send composer, and error display.
- Mounted the shell in `AppShell` as a sibling of `main`, hidden during blocking boot progress and shifted away from the workspace inspector.
- Wired `App.tsx` sends through `chatWithParaDevAi(...)` using the active project path and configured provider/model/gateway.
- Added English and Chinese chat strings plus focused SSR coverage for closed, open, blocked, and all-rail AppShell mount behavior.

Subagent notes:

- AppShell/UI inspection recommended the sibling mount after `main`, below boot progress, with stable `data-paradev-chat-*` selectors.
- API/i18n inspection confirmed the UI should call `chatWithParaDevAi(...)` directly and keep strings in the locale dictionaries.

Validation:

- `rtk npm --prefix apps/desktop run test:unit -- src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx`: 14 passed.
- `rtk npm --prefix apps/desktop run build`: passed; Vite reported the existing large-chunk warning.
- `rtk npm --prefix apps/desktop run test:unit`: 45 files passed, 583 tests passed.
- `rtk bash scripts/run.bash --tauri --port 5197`: Vite ready, Tauri dev cargo build finished, and `target/debug/paradev-desktop` launched; Computer Use could not attach to the native accessibility tree (`AXError.cannotComplete`) for screenshot inspection.

PIHC3 status: clean on `v3.1`; no PIHC3 files changed.

Next:

- Add prompt/role/source management and tool-aware AI actions for explain/create/build workflows.
