# Build Parallelism GUI Progress

Date: 2026-06-30 13:10

Linear: TAL-000

## Done

- Wired the Build page to read `paradev.build.parallelism` through the desktop config bridge.
- Added a compact translated build `Workers` control that writes the same `CM_PARADEV` key used by the SDK and CLI.
- Included configured parallelism in full and targeted `startProjectBuild` requests.
- Extended Build page, build model, and Tauri/native-web service tests for the forwarded payload.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/buildPageModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx src/buildPage/buildPageModel.test.ts src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_desktop_api_selection.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5210`

## Risks Or Blockers

- The desktop build lifecycle still has larger SDK/facade parity gaps; this slice only fixes the GUI request option that was already supported by Python build planning.

## Next

- Move the desktop build lifecycle itself behind a Python facade API or add OpenAPI/frontend operation coverage for the runtime `/desktop/builds` route cluster.
