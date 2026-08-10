# Frontend API Formless Input Contracts

Date: 2026-06-08 20:41 CST

Issues: TAL-299, TAL-295

Linear comments: TAL-299 `55386a0f-361f-4f87-81d5-aa57c85d0dd4`, TAL-295 `b40c7b1b-35cc-4e4f-8d15-ea6e6965f31b`

## Summary

This slice closes the remaining frontend API contract ambiguity from the 10:44 and 15:45 alignment reviews. The branch already reconciled the major TAL-299 planning gaps: `docs/plans/linear.md` includes TAL-299, the missing `docs/progress/2026-06-07-2345-frontend-api-contract.md` anchor exists, and the SDK browser source-path contract has tests proving canonical source rows expose loadable absolute `path` values plus project-relative `relative_path` values.

The last gap was smaller but important for frontends: several implemented operations were callable or meaningful, but had no explicit `inputs` metadata. That made "no form needed" indistinguishable from "contract row forgot to declare inputs." `project.config`, `surface.openapi`, `surface.cli_contract`, `surface.mcp_contract`, and `surface.lsp_contract` now publish `inputs=[]` deliberately. The architecture test now fails if any implemented frontend API row omits input metadata.

## Changes

- Marked the remaining form-less implemented rows with explicit `inputs=[]`.
- Added architecture coverage for `project.config` and surface contract export input rows.
- Added a global SDK contract guard: every implemented operation must declare either concrete `inputs` fields or explicit `inputs=[]`.
- Regenerated the desktop TypeScript frontend API contract. The generated Markdown reference projection was refreshed and remained byte-identical because it does not render empty input cells.
- Updated the English/Chinese frontend API manual and the architecture interface doc to describe `inputs=[]` as the canonical no-form marker.

## Review Notes

- This directly addresses the TAL-299/frontend-facing API maintenance issue called out by both alignment reviews.
- PIHC3/TAL-297 status remains a separate migration-line decision. This slice did not touch the ignored nested PIHC3 repository or move PIHC-specific assumptions into shared SDK code.
- `project.config` remains CLI-owned for broad configuration subcommands; the empty input list means "no generic GUI form," not "all config mutations are zero-argument."

## Verification

- `rtk python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 86 passed, 3 skipped because `fastapi.testclient` is unavailable in the default environment.
- `rtk npm --prefix apps/desktop run test:unit` -> 31 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py` -> passed.
- `rtk bash scripts/flake.bash --ci` -> passed.
- `rtk git diff --check` -> passed.
- Contract probe: `implemented_without_inputs []`; empty-input rows are `project.config`, `surface.frontend_api.workspace`, `surface.architecture`, `surface.openapi`, `surface.cli_contract`, `surface.mcp_contract`, and `surface.lsp_contract`.

## Next

- Continue TAL-299 by keeping the SDK operation list, generated TypeScript contract, desktop helper, REST/OpenAPI annotations, and user manual in one commit whenever a frontend-visible operation changes.
- Keep TAL-297/PIHC3 status updates on the PIHC3 migration line, while shared ParaDev core continues to focus on generic project/module/build/front-end APIs.
