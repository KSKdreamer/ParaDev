# Repo Consolidation And Test Gate

Consolidated the branch-review work onto `master` and imported the remaining template/default-asset authoring changes from the stale worktree. The branch-only remote refs were behind `master` with no unique commits; the only material ParaDev work was uncommitted in linked worktrees.

Implemented a faster standard test gate:

- `rtk bash scripts/test.bash` now runs the parallel fast suite and excludes `slow`.
- `rtk bash scripts/test.bash --full` preserves the all-tests behavior.
- `rtk bash scripts/test.bash --slow` runs the PIHC3 migration parity contracts explicitly.
- `rtk bash scripts/test.bash --serial` keeps an order-sensitive debug path.

Verification:

- `rtk bash scripts/test.bash tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture_api_selection.py tests/test_mcp_architecture_api_selectors.py tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q` passed: 13 tests.
- `rtk bash scripts/test.bash tests/test_build_registry.py tests/test_project.py tests/test_project_build.py tests/test_cli.py -q` passed: 408 tests in 18.79s.
- `rtk bash scripts/test.bash` passed: 1122 tests in 121.68s pytest time, 2m14s wall time.
- `rtk bash scripts/test.bash --full --parallel --durations=10` passed: 1386 tests in 647.50s, with the slowest PIHC3 migration contract still at 381.53s.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src tests` passed.
- `rtk uv build` passed and produced `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
