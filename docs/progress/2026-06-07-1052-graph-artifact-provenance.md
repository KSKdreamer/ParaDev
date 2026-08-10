# Graph Artifact Provenance Progress

Date: 2026-06-07 10:52

Linear: TAL-293 (read and write updates attempted; Linear connector returned `UNAUTHORIZED; Session expired. Please re-authenticate.`)

## Done

- Added `module_ids` and `collection_ids` to build graph artifact nodes when provenance can be derived from source-map sources or artifact owners.
- Carried the same graph-node provenance into build-explain graph subsets and HeavenBase `build-graph-node` preview rows.
- Updated `docs/workflows/build-flow.md` to document artifact-node provenance for graph and explanation payloads.

## Verification

- Red first: build graph, build-explain, and HeavenBase graph-node preview tests failed on missing `module_ids` and `collection_ids`.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_build_graph_returns_source_artifact_and_dependency_edges_without_writing tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_hb.py::test_hb_catalog_preview_indexes_build_graph_nodes_and_edges -q` -> 3 passed.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_build_graph_returns_source_artifact_and_dependency_edges_without_writing tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_hb.py::test_hb_catalog_preview_indexes_build_graph_nodes_and_edges tests/test_hb.py tests/test_build_manifest.py -q` -> 27 passed.
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_hb.py tests/test_build_manifest.py tests/test_cli.py -q` -> 175 passed.
- `rtk bash scripts/flake.bash --ci` -> passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/graph.py tests/test_project.py tests/test_hb.py` -> passed.
- `rtk bash scripts/test.bash` -> 270 passed.

## Risks Or Blockers

- Linear OAuth is expired in this Codex session, so issue comments cannot be created until the app is re-authenticated.

## Next

- Continue from graph/catalog traceability into generic compiler rows, especially collection-aware source-slot compilers and their user-facing diagnostics.
