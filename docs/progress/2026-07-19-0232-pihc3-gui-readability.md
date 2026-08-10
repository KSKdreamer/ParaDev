# PIHC3 GUI Readability Progress

Date: 2026-07-19 02:32

Linear: N/A

## Done

- Restored HoI4 1.19 `new_content` controls in all three PIHC country-selection entry templates.
- Added a dedicated equipment-designer stat font with black, dark green, orange, and red values while preserving the shared white inverted font used by the welcome screen and other dark panels.
- Darkened the colored event font's `§g` grey from RGB 176 to RGB 128.
- Clean-compiled and finalized PIHC3 v0.2.3.007dev in the installed mod directory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_gui_readability_contract.py tests/test_pihc3_chinese_font_contract.py tests/test_pihc3_army_hq_contract.py` (`9 passed`).
- Source and compiled startup-error contracts passed.
- Clean build emitted 18,040 modules and 37,592 artifacts with zero diagnostics and zero errors.
- Installed GUI/font definitions and launcher descriptor match the finalized build.

## Risks Or Blockers

- Pixel-level confirmation still requires opening the affected screens in HoI4; source and compiled contracts are clean.

## Next

- Recheck the country selector, equipment designers, and the iHorn event in-game.
