# AI Chat Context Safety

## Summary

- Downgraded selected AI chat entity context without a resolved source path from `source` to `workspace`, avoiding backend rejections for source descriptors with no path.
- Filtered scoped project-browser merges by the active project root so stale PIHC3 or other-project payloads cannot contaminate the active chat/browser context.
- Added a scoped-browser response commit guard that rejects late responses after the active project changes.
- Closed the PIHC3 minimization audit and queued the missing idea-category `legacy/source.yaml` cleanup as a later PIHC3 slice.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/FloatingChatShell.test.tsx src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run paradev diagnostics projects/PIHC3 --strict-metadata --json`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`
- `rtk git diff --check`
