# 2026-07-01 06:26 - AI operation navigation

## Summary

Confirmed the current environment is already aligned with HeavenBase/heaven-style 0.1.1.5: `requirements.txt`, `uv.lock`, the embedded heaven-style skill, and runtime imports all report 0.1.1.5. The focused HeavenBase/catalog/config subset passed against the installed package.

Continued the floating AI chat usability pass by making managed SDK operation cards navigation-only buttons. `module.draft` opens the existing SDK-backed module create planner for the selected/context family, while `build.plan` and `build.start` navigate only to the Build page. The cards keep `data-paradev-chat-operation-passive="true"`, never expose executable `data-paradev-operation-id`, and show explicit safety copy such as "Does not create files" and "Does not start a build." The module create intent is one-shot so closing the dialog does not leave a stale reopen trigger.

Config Models remains informational: generated AI profile operation strips stay passive `<code>` tags, not buttons.

## Verification

- `rtk uv run python - <<'PY' ...` reported HeavenBase `0.1.1.5` and confirmed the used public surfaces.
- `rtk bash scripts/sync-env.bash --check`
- `rtk uv run pytest -q tests/test_hb.py tests/test_config_api_selection.py tests/test_hb_api_selection.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/moduleEditor/ModuleEntityList.test.tsx src/components/AppShell.test.tsx src/configPage/ConfigPage.test.tsx src/App.test.ts src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47846` reached Vite ready, Cargo finished, and `target/debug/paradev-desktop` started without late startup output before manual stop.
- `rtk uv build`
