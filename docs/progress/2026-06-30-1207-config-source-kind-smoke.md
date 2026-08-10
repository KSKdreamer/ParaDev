# Config Source Kind Smoke Progress

Date: 2026-06-30 12:07 CST
Linear: active usability goal

## Done

- Hardened `config-page-smoke.html` so the rendered PIHC3-shaped Config Models page receives SDK `sourceKindRows`, including a runtime-only `project-index` row.
- Added smoke dataset fields for rendered source-kind labels, `project-index` selection state, and the Explain profile Save disabled state.
- Added stable `data-paradev-ai-profile-action` attributes for AI profile Reset and Save buttons so rendered checks do not rely on English button text or button order.
- Updated the e2e README with the five-source-row expectations and post-save disabled-state check.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts` failed because the smoke writer did not expose `aiExplainProjectIndexSelected` or `aiExplainSaveDisabled`.
- Focused checks: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts src/configPage/ConfigPage.test.tsx` passed, 44 tests.
- Rendered browser smoke at `http://127.0.0.1:5180/e2e/config-page-smoke.html`: opened Config -> Models, confirmed source kinds `project,selection,diagnostics,templates,project-index`, labels `Project,Selection,Diagnostics,Templates,Project index`, initial Explain sources `project,selection`, five toggles, toggled Templates, saved, and confirmed saved source kinds `project,selection,templates` with Save disabled again.

## Risks Or Blockers

- This smoke still uses a Vite fixture with local callbacks; it does not replace the native-web bridge smoke for real `CM_PARADEV` persistence.
- The floating AI chat remains closed in this smoke, so Config + side-docked chat layout still needs a rendered check.

## Next

- Promote `paradev.build.strict_metadata` into `CM_PARADEV` and expose it as an SDK-backed Config/BuildPage setting.
- Add a rendered Config + side-docked AI chat smoke against PIHC3 after the current smoke contract is committed.
