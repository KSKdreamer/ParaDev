# AI Source Kind Label

## Summary

- Localized the config-page label for the SDK AI chat source kind `project-index`.
- Kept the raw `project-index` value in `data-paradev-ai-profile-source-kind` so profile writes still round-trip the SDK source-kind id.
- Extended the AI profile source catalog test to cover both English and Chinese visible labels.

## Parallel Scan

The read-only GUI explorer reported three follow-up candidates:

- Add `assets` to the family-title localization lookup so asset-family build rows render consistently as localized module names.
- Localize service error messages before they appear inside translated GUI alerts.
- Surface `paradev.hoi4.launch_mode` / `paradev.hoi4.game_root` context more clearly on the Build page run controls.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx -t "SDK profile catalog"`
- `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

The PIHC3 Tauri smoke reached the Vite-ready state and launched `target/debug/paradev-desktop`; no delayed startup output appeared before stopping the process.
