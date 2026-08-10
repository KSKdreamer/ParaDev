# Python Normalizer Validation Progress

Date: 2026-06-07 09:08 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Moved from parser fidelity into the generic module compilation extension boundary.
- Found that Python-backed families validated slots, templates, settings values, required localization keys, and assets, but did not validate `settings_normalizers`.
- Added registry validation so Python-backed `settings_normalizers` must be a mapping from non-empty setting keys to callables.
- Documented the Python-backed normalizer contract in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_setting_normalizer -q` failed because the bad Python family did not raise.
- Focused green: the same command passed 1 test.
- Related project/build suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q` passed 161 tests.
- Smoke probe: `Project.load(...).families()` on a project-local Python family with `settings_normalizers={'picture': 'lower_snake'}` raised a `ProjectManifestError` with manifest path, module path, and `Build family 'notice' settings_normalizers.picture must be callable`.
- Full suite: `rtk bash scripts/test.bash` passed with 255 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Format check: `rtk bash scripts/flake.bash --check --paths src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check -- src/paradev/build/registry.py tests/test_project.py docs/workflows/build-flow.md`

## Review

- This keeps the user model unchanged: project authors still declare or register families, and invalid compiler plugins fail before discovery/build payloads are trusted.
- The validation is registry-level so both direct SDK registries and project-local Python modules share the same extension contract.
- Declarative manifests already restrict `settings_normalizers` to named strategies; this slice covers the Python-backed path.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- Python normalizer functions can still raise non-`ValueError` exceptions during normalization; deciding whether to wrap all exceptions needs a separate error-boundary decision.

## Next

- Continue generic compiler hardening by checking other project-local Python extension hooks against declarative manifest validation, then return to user-facing compiler inspection and diagnostics.
