# Linear Plan Sync

Status: active sync map

Date: 2026-06-08

Workspace: `Talirian`

Project: `ParaDev`

Local source: [../goals/short-term-plan.md](../goals/short-term-plan.md)

## Active Foundation Issues

| Issue | Title |
| --- | --- |
| [TAL-290](https://linear.app/talirian/issue/TAL-290/foundation-integrate-heavenbase-cli-and-config-contracts) | Foundation: integrate HeavenBase CLI and config contracts |
| [TAL-291](https://linear.app/talirian/issue/TAL-291/foundation-implement-pdx-tokenizer-ast-formatter-and-round-trip-tests) | Foundation: implement PDX tokenizer, AST, formatter, and round-trip tests |
| [TAL-292](https://linear.app/talirian/issue/TAL-292/foundation-implement-paradevyaml-project-loading-and-source-discovery) | Foundation: implement paradev.yaml project loading and source discovery |
| [TAL-293](https://linear.app/talirian/issue/TAL-293/foundation-implement-build-graph-records-and-manifests) | Foundation: implement build graph records and manifests |
| [TAL-294](https://linear.app/talirian/issue/TAL-294/foundation-implement-metadata-pdx-localization-and-copy-slot-compilers) | Foundation: implement metadata, PDX, localization, and copy slot compilers |
| [TAL-296](https://linear.app/talirian/issue/TAL-296/foundation-ship-first-sdkcli-usable-package-workflow) | Foundation: ship first SDK/CLI usable package workflow |
| [TAL-298](https://linear.app/talirian/issue/TAL-298/foundation-add-sdk-module-template-scaffolding) | Foundation: add SDK module template scaffolding |
| [TAL-297](https://linear.app/talirian/issue/TAL-297/pihc3-bootstrap-clean-project-skeleton-and-parity-baseline) | PIHC3: bootstrap clean project skeleton and parity baseline |

## Continuous Stewardship Issues

| Issue | Title | Local anchor |
| --- | --- | --- |
| [TAL-295](https://linear.app/talirian/issue/TAL-295/continuous-maintain-hoi4-modder-user-manual) | Continuous: maintain HoI4 modder user manual | [../user-manual/](../user-manual/) |
| [TAL-299](https://linear.app/talirian/issue/TAL-299/foundation-maintain-frontend-api-contract) | Foundation: maintain frontend API contract | `codex/frontend-api-master-reconcile`, [../architecture/interfaces.md](../architecture/interfaces.md), [../user-manual/frontend-api.md](../user-manual/frontend-api.md), [../user-manual/frontend-api-reference.md](../user-manual/frontend-api-reference.md) |

## Sync Note

On 2026-06-07, the `codex_apps` Linear connector returned `UNAUTHORIZED; Session expired. Please re-authenticate.`, but the `mcp__linear` connector successfully created TAL-295, TAL-296, and TAL-297. If future Linear updates fail, retry with the working connector or refresh OAuth.

On 2026-06-08, TAL-298 had moved beyond the original Python-only slice: `Project.create_module(...)` remains the minimal SDK verb, while `paradev templates`, `paradev scaffold`, REST draft creation, and desktop SDK-backed creation now share the same authoring-template contract. Rendered React create/apply coverage and the installed Python-wheel host smoke cover the GUI path without mutating PIHC3. Remaining TAL-298 work should focus on more PIHC3 authoring templates, shared-family cleanup, and replacing any lingering local fallbacks with SDK-backed bridges as those SDK payloads mature.

On 2026-06-08, the 10:44 and 15:45 alignment reviews were reconciled on the `master` line. The SDK browser source-path contract is fixed and tested by `tests/test_project.py::test_project_browser_canonical_sources_are_project_readable`; canonical rows now expose a project-readable `path` and project-relative `relative_path`. `TAL-299` is now represented in this planning map, but its generated frontend API reference and TypeScript contract remain on `codex/frontend-api-master-reconcile` until that branch is reviewed against current PIHC3 import work and reruns the full Python, desktop, package, and generated-reference gates.

On 2026-06-08, TAL-297 gained a native PIHC3 event namespace slice: 41 normal `resources/events/<namespace>` roots now import into `projects/PIHC3/src/modules/event`, preserving compiled PIHC_dev PDX and consolidated English/Simplified Chinese localization. The PIHC3 build now reports 870 modules, 25,313 artifacts, 0 diagnostics, and `blocked: false`; `BCE`, `SUPER`, `SUPER_NEWS`, event images, sprites, and date-triggered on-action parity remain future work.

On 2026-06-08, TAL-297 also gained a native PIHC3 character slice: 250 `resources/characters/<TAG>` roots now import into `projects/PIHC3/src/modules/character`, preserving compiled PIHC_dev PDX and English/Simplified Chinese localization while listing portrait/animation evidence without copying the large binary asset set. The PIHC3 build now reports 1,120 modules, 25,313 artifacts, 0 diagnostics, and `blocked: false`; generated portraits, portrait sprites, random characters, animation strips, role-specific templates, and parity review remain future work.

On 2026-06-08, TAL-297 gained a native PIHC3 focus-tree slice: 28 `resources/focuses/<TREE>` roots now import into `projects/PIHC3/src/modules/focus_tree`, preserving compiled PIHC_dev `common/national_focus/<TREE>.txt` PDX and consolidated English/Simplified Chinese focus localization while listing focus icon evidence without copying icon binaries. The PIHC3 build now reports 1,148 modules, 25,351 artifacts, 0 diagnostics, and `blocked: false`; focus icon DDS generation, sprite declarations, per-node editable source reconstruction, GUI layout review, exact no-focus guard policy, and parity review remain future work. The user-facing `focus` template remains the compact path for adding one new focus node.

On 2026-06-08, TAL-297 gained a native PIHC3 decision slice: 62 `resources/decisions/<CATEGORY>` roots now import into `projects/PIHC3/src/collections/decision`, and 458 decision folders now import into `projects/PIHC3/src/modules/decision`. The importer preserves compiled PIHC_dev category descriptors and decision PDX, normalizes English/Simplified Chinese localization, records source provenance, and excludes reviewed legacy decision outputs from the copy overlay to avoid duplicate definitions. The PIHC3 build now reports 1,606 modules, 62 collections, 25,355 artifacts, 0 diagnostics, and `blocked: false`; decision icon DDS generation, category/decision sprite declarations, scripted GUI parity, category authoring helpers, and editable per-decision source reconstruction remain future work. The user-facing `decision` template remains the compact path for adding one basic decision.

On 2026-06-08, the five-hour alignment reviews identified `TAL-299` as a missing master-line planning row while the frontend-facing API implementation originated on `codex/scaffold-source-root-selection`. The reconciled TAL-299 integration branch is now `codex/frontend-api-master-reconcile`; keep review and follow-up work there until it is merged deliberately. PIHC3 status and importer work remain owned by the PIHC3 migration line, not by shared ParaDev SDK planning.

## Current Drift Notes

- `TAL-299` frontend-facing API work originated on `codex/scaffold-source-root-selection` and is being reconciled on branch `codex/frontend-api-master-reconcile`. The initial local anchor is [../progress/2026-06-07-2345-frontend-api-contract.md](../progress/2026-06-07-2345-frontend-api-contract.md).
- `TAL-297` remains a PIHC3 parity/status reconciliation item owned by the PIHC3 migration line. ParaDev core agents should keep shared SDK and compiler behavior generic and avoid moving PIHC3-specific importer assumptions into `src/paradev`.
- Alignment reviews on 2026-06-08 called out repo-line divergence between `master` and `codex/scaffold-source-root-selection`; keep the reconciliation branch reviewable and rerun the full Python, desktop, and package gates before merge.

## Cleanup Note

On 2026-06-06, 232 unarchived closed or duplicate legacy issues were removed from the requested Linear projects to free issue capacity:

- HeavenBase: 124
- ParaDev: 94
- PIHC: 14
- RubikSQL: 0

## Sync Rule

When a local planning file and Linear diverge, update both in the same work loop. Linear owns current execution status; local docs own durable architecture and acceptance criteria.
