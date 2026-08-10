# Review Wrap-Up And TAL-299 Sync

Date: 2026-06-08 21:04 CST

Linear: TAL-295, TAL-297, TAL-299

## Done

- Addressed the 10:44 alignment review by confirming the SDK browser source-path bug is already fixed on `master`: `Project.browser()` resolves canonical slot sources through module or collection roots, and `tests/test_project.py::test_project_browser_canonical_sources_are_project_readable` guards absolute `path` plus project-relative `relative_path`.
- Addressed the 15:45 alignment review by adding `TAL-299` to `docs/plans/linear.md` while keeping the frontend API implementation branch separate from the PIHC3 import line.
- Kept `TAL-297` open in docs because PIHC3 is buildable and no longer untouched, but parity gaps remain. Current notes show imported technology, event, character, focus-tree, and decision slices with zero diagnostics.
- Preserved branch ownership: `master` carries PIHC3 import progress; `codex/frontend-api-master-reconcile` carries the generated frontend API/manual/reference work and still needs a gated reconciliation before merge.
- Posted Linear comments: `TAL-297` comment `5e5c0d1b-2c87-4e37-8126-69eb54db7ea3`; `TAL-299` comment `7b9c67d2-9596-4cdd-9401-6d56740e3559`.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py::test_project_browser_canonical_sources_are_project_readable -q`: passed, 1 test.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: passed, 60 tests.
- `rtk uv run paradev summary projects/PIHC3 --json`: passed with 1,606 modules, 62 collections, 25,355 artifacts, 0 diagnostics, and `blocked: false`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: passed with no diagnostics.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`: passed, 2 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- The app-scoped Linear connector still returns an expired-session error; use the direct `mcp__linear` comment tool until OAuth is refreshed.
- `projects/PIHC3` is an ignored nested repo and remains a separate checkout from parent ParaDev. Parent docs/tests that depend on it need both repos in the expected state.
- Frontend API branch reconciliation is intentionally deferred; the branch is large and should not be merged without full backend/frontend/package gates.
- Local `.codex-artifacts/` and `.playwright-mcp/` files remain automation artifacts and should not be staged.

## Next

- Rebase or merge `codex/frontend-api-master-reconcile` onto current `master` in a dedicated pass, then rerun full Python, desktop, package, generated-reference, and review gates.
- Continue PIHC3 migration through importer/parity slices rather than scaffold-only claims.
