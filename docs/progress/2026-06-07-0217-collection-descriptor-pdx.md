# 2026-06-07 02:17 CST - Collection Descriptor PDX

## Done

- Made generic `CollectionSourceFamily` prepend collection descriptor PDX entries before member module PDX entries.
- Tracked descriptor PDX files as collection artifact inputs and source-map sources.
- Kept focus-style `CollectionPDXFamily` module-driven while enabling descriptor PDX for generic collection-source compilers.
- Documented the descriptor PDX ordering and source-map contract in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_source_family_includes_descriptor_pdx_in_collection_artifact -q` failed because the collection artifact only included the module `def.pdx`.
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_source_family_includes_descriptor_pdx_in_collection_artifact tests/test_project_build.py::test_project_build_uses_registered_collection_source_slots -q` passed 2 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py tests/test_module_sources.py -q` passed 97 tests.
- Full suite: `rtk bash scripts/test.bash` passed 160 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_simple_source_family.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python -c "from pathlib import Path; from tempfile import TemporaryDirectory; ..."` confirmed descriptor `category.txt` is the first collection artifact input and source-map source.
- Whitespace: `rtk git diff --check -- src/paradev/build/families.py tests/test_simple_source_family.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0217-collection-descriptor-pdx.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Descriptor PDX is enabled for generic collection-source families only. Focus-specific collection PDX remains module-driven until a profile explicitly needs descriptor PDX there.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue tightening generic family contracts so collection descriptors, module sources, source maps, and artifact writers stay aligned.
