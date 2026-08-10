# Project Python Registry Modules Progress

Date: 2026-06-07 04:00 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Added `python_modules` to `paradev.yaml` loading as trusted project-local Python registry modules.
- Validated module paths at project load time: entries must be non-empty `.py` files under the project root.
- Added registry module execution through `register(registry)`, supporting mutation in place or returning a `BuildRegistry`.
- Preserved explicit SDK `registry=` behavior: caller-supplied registries bypass manifest registry extensions.
- Documented `python_modules` in the manifest schema note and build-flow guide.

## Verification

- Red check: focused tests failed before implementation because `python_modules` was ignored, missing files were accepted, and missing `register(registry)` did not fail.
- `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_python_registry_module tests/test_project.py::test_project_manifest_rejects_missing_python_module tests/test_project.py::test_project_families_rejects_python_module_without_register -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/build/extensions.py src/paradev/build/__init__.py tests/test_project.py tests/test_project_build.py`
- `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/build/extensions.py src/paradev/build/__init__.py tests/test_project.py tests/test_project_build.py docs/resources/05-project-manifest.md docs/workflows/build-flow.md docs/progress/2026-06-07-0400-project-python-registry-modules.md`
- SDK smoke probe loaded a temporary project with `tools/families.py`, exposed a custom `notice` family, and planned `common/notices/GER_notice.txt`.

## Risks Or Blockers

- Python registry modules are trusted local project code; this is appropriate for project extensions but should not be used for untrusted project inspection.
- Linear status could not be updated from this environment.

## Next

- Continue moving generic compiler behavior into reusable family contracts before adding more domain-specific HOI4 slots.
- Add a follow-up issue when Linear access is available for safer plugin packaging, import diagnostics, and extension discovery UX.
