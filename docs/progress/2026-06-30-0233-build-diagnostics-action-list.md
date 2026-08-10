# Build Diagnostics Action List

## Summary

- Added a compact blocked-diagnostics list to the Build page so modders see the exact SDK diagnostic message, code, module or collection target, and source path before trying to build.
- Kept warnings in the diagnostics metric while showing only blocking errors in the overview action list.
- Added English and Chinese translations plus focused styling that fits the existing workbench surface.
- Recorded follow-up audit candidates for config number editing and AI chat context safety from read-only subagents.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx src/buildPage/buildPageModel.test.ts src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run paradev diagnostics projects/PIHC3 --strict-metadata --json`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`
- `rtk git diff --check`
