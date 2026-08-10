# Project inspection index helper

## Scope

- Reused `append_index_entry()` for the project inspection filter index.
- Removed the last local `setdefault(...).append(...)` pattern from `src/paradev/sdk/project.py`.
- Kept the project inspection contract and generated reference markdown output unchanged.

## Verification

- `rtk gh pr status`
- `rtk uv run python - <<'PY' ... PY` project inspection contract/reference comparison with `HEAD`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes -q`
- `rtk uv run python -m py_compile src/paradev/sdk/project.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py`
- `rtk git diff --check -- src/paradev/sdk/project.py`

Full-suite tests were skipped to keep CPU available for PIHC3 migration workers. GitHub reported no current PRs, so there were no review threads to address directly.
