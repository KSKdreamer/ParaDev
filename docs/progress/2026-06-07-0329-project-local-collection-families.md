# 2026-06-07 03:29 CST - Project-Local Collection Families

## Done

- Extended `paradev.yaml` project-local family declarations from `simple_source` to `collection_source`.
- Wired declarative collection source slots, collection PDX templates, optional uncollected module PDX templates, localization templates, metadata contracts, settings contracts, localization key contracts, and asset constraints into the generic `CollectionSourceFamily`.
- Added SDK/build coverage for a manifest-declared `news_event` family with module-owned PDX, collection-owned descriptor PDX, and collection-owned localization.
- Rejected `module_pdx` templates and `collection_source_slots` on `simple_source` families so collection-only manifest fields cannot become silent no-ops.
- Updated the build-flow guide with a collection-family YAML example and the user-facing behavior for descriptor PDX, descriptor localization, and `module_pdx` fallback.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family -q` failed because `families.news_event.kind` only accepted `simple_source`.
- Validation red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_manifest_rejects_module_pdx_template_for_simple_family -q` failed because simple families silently accepted `module_pdx`.
- Validation red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_manifest_rejects_collection_slots_for_simple_family -q` failed because simple families silently accepted `collection_source_slots`.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project.py::test_project_manifest_rejects_unsupported_family_kind tests/test_project.py::test_project_manifest_rejects_module_pdx_template_for_simple_family tests/test_project.py::test_project_manifest_rejects_collection_slots_for_simple_family -q` passed 5 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q` passed 101 tests.
- Full suite: `rtk bash scripts/test.bash` passed 174 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python - <<'PY' ...` loaded a temporary project with a manifest-declared `news_event` collection family and planned `events/germany.txt` plus `localisation/english/germany_l_english.yml`.

## Review

- Reviewed the intentional diff for manifest extension validation, generic collection-family registration, SDK/build coverage, and build-flow docs; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Declarative project-local families now cover generic `simple_source` and `collection_source`; routed families and custom Python-backed compilers remain later extension points.
- Explicit SDK `registry=` arguments remain authoritative and do not merge `paradev.yaml` family declarations.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Move the declarative path toward routed settings where generic helpers are still enough, then define the Python plugin loading contract for custom compiler modules.
