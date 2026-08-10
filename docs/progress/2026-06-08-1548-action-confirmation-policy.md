# Action Confirmation Policy Progress

Date: 2026-06-08 15:48

Linear: TAL-299, TAL-295

Alignment reviews: `2026-06-08-1044-five-hour-alignment-review.md`, `2026-06-08-1545-five-hour-alignment-review.md`

## Done

- Added SDK-owned `paradev.sdk.frontend-api.confirmation.v1` metadata to workspace action execution rows.
- Marked non-local mutating actions as confirmation-required, with `scope`, `style`, `title`, `summary`, `confirm_fields`, and `default_confirmed`.
- Updated the desktop helper and Run control so ready REST-plan execution stays disabled while confirmation is required.
- Regenerated the TypeScript and Markdown frontend API contracts, and updated English/Chinese manuals plus architecture/UI docs.
- Addressed alignment-review planning drift by adding TAL-295 and TAL-299 stewardship rows to `docs/plans/linear.md`, and importing the two five-hour alignment review notes into this branch.
- Added browser contract assertions for the current branch shape: `Project.browser()` module items expose an absolute module `root`, while `source_slots` remain owner-relative paths that resolve under that root.
- Linear comments posted: TAL-299 `eb04ca17-0ab8-4545-b334-928693ef585f`, TAL-295 `fccafca4-fb40-4314-b4cd-2da94789c95c`, TAL-297 `f3559dbf-00dc-4a7a-b596-2a1bdbcf0098`.

## Verification

- Focused confirmation and desktop Run-gating guards passed: `4 passed`.
- CLI probes for `module.remove --action` and `project.state --action` showed the expected confirmation payloads.
- Focused wrap-up guards passed: `6 passed`, covering confirmation policy, desktop Run gating, generated reference parity, and the current `Project.browser()` source-root/source-slot contract.
- Desktop build passed: `rtk npm --prefix apps/desktop run build`.
- Static gates passed: `rtk bash scripts/flake.bash --ci`, `rtk git diff --check`, and Heaven-style scan on the changed Python paths.
- Broad Python suites passed: `tests/test_architecture.py tests/test_cli.py tests/test_project.py -q` reported `240 passed`.
- Full Python suite passed: `501 passed`.
- Package build passed: `rtk uv build`.
- Browser smoke on `http://127.0.0.1:5174?smoke=confirmation-policy` reported zero console errors; the temporary Vite server was stopped afterward.

## Risks Or Blockers

- A dedicated confirmation UI is still a follow-up before mutating Run flows can be enabled.
- The desktop REST bridge transport is still pending.
- The 10:44 browser source-row bug described a newer module-editor/master-line implementation that is not present in this frontend API branch. This branch now tests its current browser root/source-slot contract; the source-row fix still belongs with the master/module-editor reconciliation if that implementation is merged here.
- TAL-297 status belongs to the PIHC3 migration line. This branch records the drift but does not move PIHC3-specific status or importer behavior into ParaDev core.

## Next

- Add the confirmation UI flow that can satisfy `execution.confirmation`.
- Wire the desktop REST bridge transport after the confirmation path is visible.
- Reconcile `master` and `codex/scaffold-source-root-selection` explicitly before merging either line.
