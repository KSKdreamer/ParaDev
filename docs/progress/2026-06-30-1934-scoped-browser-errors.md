# Scoped Browser Errors Progress

Date: 2026-06-30 19:34

Linear: continuous usability goal

## Done

- Tracked scoped project-browser load failures per workspace tab key instead of only logging them to the console.
- Passed active and secondary pane load errors through AppShell and Workspace into ModuleEditor.
- Rendered scoped SDK load failures as a distinct `role="alert"` state before the generic SDK-unavailable fallback.
- Kept stale errors hidden once the scoped browser payload is present after a retry or cache refresh.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "scoped browser load errors"` failed before the fix because the helper did not exist.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEditor.test.tsx -t "scoped SDK load failures"` failed before the fix because ModuleEditor rendered the generic unavailable fallback.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "scoped browser load errors"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEditor.test.tsx -t "scoped SDK load failures"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning.
- Tauri smoke was stopped after launch with Ctrl-C, producing the expected code 130.

## Next

- Address AI chat profile load failures silently removing roles/prompts.
- Consider the PIHC3 flag metadata cleanup candidate from the minimization audit.
