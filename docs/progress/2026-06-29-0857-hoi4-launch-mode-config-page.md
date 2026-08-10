# 2026-06-29 08:57 - HOI4 Launch Mode Config Page

## Slice

- Added `paradev.hoi4.launch_mode` to the Config page Projects section as the persistent SDK-backed HOI4 launch setting.
- Extended `ConfigPageSettings` normalization with a typed `steam | local` launch mode default.
- Wired desktop config reads and writes through `applyDesktopConfigValuesToConfigPageSettings` and `desktopConfigWritesForSettingsChange`.
- Added English and Chinese Config-page translations separate from the Build-page action labels.

## Verification

- Red checks first:
  - `rtk bash -lc 'cd apps/desktop && npm test -- src/configPage/ConfigPage.test.tsx src/App.test.ts'`
- Green/final checks:
  - `rtk bash -lc 'cd apps/desktop && npm test -- src/configPage/ConfigPage.test.tsx src/App.test.ts'`
  - `rtk npm --prefix apps/desktop run test:unit`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`

## Tauri Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Verified the native Config page opens with PIHC3 project paths and SDK counts, not demo data.
- Verified the Projects page shows translated `HOI4 启动方式`, `paradev.hoi4.launch_mode`, `HOI4 游戏目录`, and `paradev.hoi4.game_root` rows without clipping.
- Exercised the launch-mode selector from `Steam 启动器` to `本地应用`, then restored it to `Steam 启动器`.
- Confirmed the Python SDK reads the restored value:
  - `rtk uv run python -c "from paradev.desktop import desktop_read_config_value; print(desktop_read_config_value('paradev.hoi4.launch_mode'))"`
- Screenshots:
  - `/tmp/paradev-tauri-hoi4-launch-mode-config-page.png`
  - `/tmp/paradev-tauri-hoi4-launch-mode-dropdown.png`
  - `/tmp/paradev-tauri-hoi4-launch-mode-local-selected.png`
  - `/tmp/paradev-tauri-hoi4-launch-mode-restored.png`
