# Open Path Default Parity Progress

Date: 2026-06-30 07:29

Linear: active goal

## Done

- Investigated the API/GUI drift reported by the alignment explorer: the GUI defaults Linux and unknown platforms to Cursor, while the Python desktop facade routed empty or legacy `default` targets to Finder outside Windows.
- Added Python regression coverage for `None` and `default` open-path targets across macOS, Windows, Linux, and unknown platform labels.
- Added frontend guard coverage for Linux and unknown target ordering/default normalization.
- Updated the Python desktop facade so empty and legacy `default` targets resolve through the same platform default contract as the GUI picker: Finder on macOS, Explorer on Windows, Cursor elsewhere.

## Verification

- `rtk uv run pytest tests/test_desktop_api_selection.py -k open_path` failed first on the Windows `default` alias routing to Finder, then passed after the facade fix.
- `rtk npm --prefix apps/desktop run test:unit -- src/openPathTargets.test.ts`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/shell.py tests/test_desktop_api_selection.py`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`

## Risks Or Blockers

- The GUI still has local icon/label metadata for open-path targets; this slice aligns behavior but does not generate the target catalog from Python yet.

## Next

- Consider adding a Python-owned open-path target catalog/API so future GUI metadata and Python command planning cannot drift silently.
