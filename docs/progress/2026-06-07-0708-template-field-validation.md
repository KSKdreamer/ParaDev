# Template Field Validation Progress

Date: 2026-06-07 07:08 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added load-time placeholder validation for declarative project-local family templates.
- Covered simple, routed, collection, sprite GFX, sprite-name, and required localization-key templates with context-specific supported field sets.
- Added a manifest regression test that rejects an unknown `templates.copy` placeholder during `Project.load(...)`.
- Documented the new user-facing manifest validation behavior in the build workflow.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_unknown_family_template_fields -q` failed because `Project.load(...)` did not raise `ProjectManifestError`.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_unknown_family_template_fields -q`
- Related project suites: `rtk uv run pytest tests/test_project.py tests/test_project_build.py -q` passed with 115 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 230 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`

## Review

- Bad placeholders now fail at manifest load with the manifest path, family path, template key, unknown field, and supported fields.
- Collection `loc` and `copy` templates are intentionally limited to fields available to both descriptor-owned and member-module outputs.
- The first heaven scan attempt without `uv run` failed because `heavenbase` was not importable; the uv-backed scan passed.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening declarative family ergonomics around route settings and generic compiler diagnostics.
- Move toward the generic module compilation system once manifest authoring failures are consistently early and contextual.
