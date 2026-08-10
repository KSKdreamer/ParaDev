# Master TAL-299 Linear Sync

Date: 2026-06-08 19:07 CST

Linear: `TAL-299` comment `5866783c-f29d-43a1-8121-b5746fb28456`, `TAL-295` comment `0f0d0495-d331-4787-8d47-1960e0d3c5a5`

## Done

- Added `TAL-299` to the master-line Linear sync map as a continuous stewardship issue for the frontend API contract.
- Recorded that `codex/scaffold-source-root-selection` remains the TAL-299 implementation branch until deliberate reconciliation with `master`.
- Imported the 2026-06-08 15:45 five-hour alignment review note into this branch's tracked progress folder.
- Left PIHC3 importer/test work untouched because it belongs to the separate migration line.

## Verification

- `rtk rg -n "TAL-299|codex/scaffold-source-root-selection|2026-06-08 15:45" docs/plans/linear.md docs/progress`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed, 62 Python files.
- `rtk uv run paradev summary demos/assets/projects/minimal --json`: passed with 1 module, 1 collection, 5 artifacts, 0 diagnostics, and `blocked=false`.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q -k 'not rest_create_module_draft_uses_sdk_template_family_resolution'`: passed, 11 tests, 1 skipped, 1 deselected.

## Risks Or Blockers

- The frontend API code remains on `codex/scaffold-source-root-selection`; this sync does not merge or validate that branch against current `master`.
- The root `/Users/magolor/Utils/ParaDev-3` worktree still has unrelated PIHC3 character-importer test changes and local browser artifacts.
- Full `tests/test_architecture.py` failed in this clean worktree because ignored nested `projects/PIHC3` is absent here. The original root worktree does have `projects/PIHC3`, but it is a separate dirty nested migration repo, so this docs-only branch did not link or copy it.

## Next

- Reconcile `codex/scaffold-source-root-selection` with `master` in a dedicated branch when the team is ready to merge TAL-299 code.
- Keep shared SDK/API docs synchronized with GUI and PIHC3 proposals without moving project-specific importer behavior into `src/paradev`.
