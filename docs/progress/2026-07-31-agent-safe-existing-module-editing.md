# Agent-safe Existing-module Editing

Date: 2026-07-31

## Outcome

- Audited the live PIHC3 Registry rather than extension folder names:
  - 72 registered build families;
  - 51 ordinary visible families, all 51 with at least one authoring-ready
    template;
  - 21 intentionally hidden low-level families;
  - editable extension-registered Focus, Technology, Doctrine, and MIO diagram
    providers.
- Added `project_browser` and `module_file` to the bounded
  `paradev mcp serve` runtime. Agents can now discover an exact module through
  Registry-owned family/source contracts and read one UTF-8 source without
  shell access.
- `Project.read_module_file(...)` now returns `size` and string-valued
  `mtime_ns` from the same stable descriptor-backed snapshot as `text`.
  `project_draft_apply` accepts those values as its existing
  `expected_size`/`expected_mtime_ns` guard, so an external edit blocks the
  whole agent draft rather than being overwritten.
- Updated the project-owned `paradev-authoring` skill with separate creation,
  existing-module edit, and graph-edit workflows. The skill requires one
  revision-guarded transaction for related source edits and folder-title
  synchronization.
- Synced the authoring architecture and bilingual module manual.

## PIHC3 Structure Evidence

- `tests/test_pihc3_extensible_layout.py` still proves:
  - no `_component` or `_asset_component` directories;
  - no `legacy`, `legacy-source.yaml`, or `inactive_modules`;
  - every source unit uses `id - preferred title`;
  - visible metadata is limited to `collection`, `inactive`, and `comment`;
  - system settings remain in module-local `.paradev/meta.yaml`;
  - every visible Registry family is Entity/template owned by PIHC3.
- The focused PIHC3 extensibility/consolidation suite is green: 28 tests.
- A real MCP read resolved
  `idea/IDEA_ALL_ARTIFACT_ALICORN_AMULET` through its titled Chinese folder and
  returned a non-empty stable `def.txt` snapshot.
- A strict dry module-partial build remains clean: 1 module, 0 collections,
  10,997 artifacts, 0 diagnostics.

## Verification

- `tests/test_mcp_authoring.py`, `tests/test_project.py`, and
  `tests/test_architecture.py`: 440 passed.
- Full fast Python gate: 2,219 passed, 9 native-Windows skips.
- Heaven-style scan: the changed MCP surface is clean; the broader selected
  scan reports only established imports in pre-existing large modules/tests.
- Flake8 on changed Python/test files: clean.
- Python byte compilation: clean.
- `git diff --check` on the touched slice: clean.
- `skill-creator` quick validation: `paradev-authoring` is valid.

## Remaining

- MCP existing-module editing is intentionally UTF-8 text only. Binary
  replacements remain available through the existing transactional draft
  contract but need a separately bounded read/preview workflow before agents
  should author them.
- A future MCP slice can expose SDK-owned guided source forms for lower-burden
  field edits; raw PDX remains the required escape hatch.
