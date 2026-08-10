# Mod Descriptor Preview Progress

Date: 2026-06-07 16:09

Linear: TAL-296, TAL-295

## Done

- Added HOI4 project-owned `mod_descriptor` artifacts for `descriptor.mod` and `.paradev/build/launcher/<project_id>.mod`.
- Added `ModDescriptorWriter` through the normal build registry instead of writing descriptor files from CLI or SDK surface code.
- Passed project title and output/build roots through `BuildContext.metadata` for profile-owned project artifacts.
- Updated CLI, SDK, build-flow, and bilingual user/developer manual docs for descriptor preview output paths.

## Verification

- Red test: `rtk uv run pytest tests/test_project_build.py::test_hoi4_profile_emits_project_descriptor_and_launcher_preview` failed with no planned descriptor artifacts.
- Green test: `rtk uv run pytest tests/test_project_build.py::test_hoi4_profile_emits_project_descriptor_and_launcher_preview`
- Targeted subset: `rtk uv run pytest tests/test_project_build.py tests/test_cli.py tests/test_sdk_examples.py`
- HB/project regression subset: `rtk uv run pytest tests/test_hb.py tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_demo_project_build_cli_outputs_profile_artifacts tests/test_project.py::test_project_summary_returns_manifest_payload_without_writing tests/test_project.py::test_project_cli_outputs_summary_manifest_json_without_writing tests/test_project.py::test_project_manifests_returns_all_manifest_payloads_without_writing tests/test_project.py::test_project_cli_outputs_all_manifest_payloads_without_writing tests/test_project.py::test_demo_project_build_cli_can_emit_profile_files tests/test_project.py::test_demo_project_build_cli_can_emit_source_map_manifests`
- Smoke probes: `rtk uv run paradev summary demos/assets/projects/minimal --json`, `rtk uv run paradev artifacts demos/assets/projects/minimal --type mod_descriptor --json`, and temp-project `paradev new` plus `paradev build --emit-artifacts --emit-manifests`.
- Style and docs: heaven-style scan on changed Python paths, `rtk git diff --check`, `rtk bash scripts/flake.bash --ci`, and manual local-link check.
- Full gate: `rtk bash scripts/test.bash` (`335 passed`) and `rtk uv build`.

## Risks Or Blockers

- Linear connector still returns `UNAUTHORIZED; Session expired. Please re-authenticate.` for TAL-296 and TAL-295, so status comments could not be posted from this session.
- The launcher `.mod` is a preview under `.paradev/build/launcher/`; ParaDev still does not install it into the user's HoI4 launcher folder.

## Next

- Run style, lint, package, and full test gates.
- Continue TAL-296 toward install/export ergonomics and PIHC3 bootstrap prerequisites.
