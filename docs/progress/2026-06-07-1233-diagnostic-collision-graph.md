# Diagnostic Collision Graph Progress

Date: 2026-06-07 12:33

Linear: TAL-294

## Done

- Added diagnostic-code build explanations for artifact collisions to return exact artifact graph context instead of an unanchored empty graph.
- Let artifact-target graph filters include artifact-only nodes when planned artifacts have no source-slot inputs.
- Merged duplicate artifact graph nodes by output location, aggregating `owners`, `module_ids`, and `collection_ids` for collision explain payloads.
- Documented the collision graph behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_scopes_diagnostic_artifacts_by_target_root -q` failed with `graph_node_count` still `0`.
- Green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_scopes_diagnostic_artifacts_by_target_root -q` passed.
- Related: `rtk bash scripts/test.bash tests/test_project.py -q` passed, `95 passed`.
- Related cluster: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py -q` passed, `116 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/graph.py src/paradev/build/explain.py tests/test_project.py` passed, `OK: 3 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `289 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue tightening generic module compilation inspection around source slots, artifact writers, and diagnostics.
