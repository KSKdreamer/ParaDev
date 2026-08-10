# 2026-06-08 18:06 Rendered Create/Apply Smoke

## Scope

- Added a repeatable Vite-rendered desktop smoke fixture for the template-backed module create/apply flow.
- Kept production `index.html` unchanged.
- Used a mocked Tauri invoke bridge so the real React app can exercise the same `paradev_desktop_state`, `paradev_create_module_draft`, and refresh behavior in the in-app Browser.

## Fixture

- `apps/desktop/e2e/module-create-smoke.html`
- `apps/desktop/e2e/README.md`

The fixture exposes a PIHC3 project state with a project-local `focus` template. The rendered UI opens the Focus module, creates `FOCUS_RENDERED_FRIENDSHIP`, applies it with `write: true`, then refreshes browser state so the entity becomes a clean canonical row with `meta`, `def`, and `loc` source slots.

## Browser Evidence

- URL: `http://127.0.0.1:5180/e2e/module-create-smoke.html`
- Title: `ParaDev Module Create Smoke`
- Console warnings/errors: none.
- Initial DOM: nonblank desktop shell, PIHC3 project selected, Focus module available from template payload.
- Create interaction: filled object id, title, and description; clicked New; row appeared selected as `新建草稿`.
- Apply interaction: clicked Apply; row refreshed to clean `未修改`, canonical, 3 source files, and path `src/modules/focus/FOCUS_RENDERED_FRIENDSHIP`.
- Machine-readable bridge proof: `data-paradev-e2e-command-count="5"` and `data-paradev-e2e-write-count="1"` on the HTML element after the flow.
- Screenshot captured in the in-app Browser after Apply.

## Verification

- `rtk npm --prefix apps/desktop run dev -- --port 5180`
- Browser smoke through the in-app Browser plugin.
- `rtk npm --prefix apps/desktop run test:model`: 2 files, 14 tests passed.
- `rtk npm --prefix apps/desktop run build`: TypeScript and Vite build passed.
- `rtk git diff --check && rtk git -C projects/PIHC3 diff --check`: passed.
- `curl -sSf http://127.0.0.1:5180/e2e/module-create-smoke.html`: returned the Vite-served fixture with the smoke title and mock project root.

## Remaining Risk

- This is rendered React coverage with a mocked Tauri bridge. It does not replace the Rust command tests or a real packaged Tauri app run.
- The real filesystem write path is still owned by Python SDK tests, CLI probes, and Tauri command tests.
