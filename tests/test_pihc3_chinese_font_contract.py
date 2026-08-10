from pathlib import Path

from heavenbase.utils import exists_file, load_bin, load_txt

PIHC3_ROOT = Path("projects/PIHC3")


def _module_root(family: str, object_id: str) -> Path:
    matches = tuple((PIHC3_ROOT / "src/modules" / family).glob(f"{object_id} - *"))
    assert len(matches) == 1
    return matches[0]


INTERFACE_ROOT = _module_root("interface", "INTERFACE_PIHC_INTERFACE") / "interface"
FONT_ROOT = _module_root("font", "FONT_PIHC_FONTS") / "gfx/fonts"


def test_pihc3_colored_event_font_has_base_and_chinese_override() -> None:
    core = load_txt(str(INTERFACE_ROOT / "core.gfx"), encoding="utf-8")
    chinese = load_txt(str(INTERFACE_ROOT / "core_chinese.gfx"), encoding="utf-8")

    assert 'bitmapfont = {\n\t\tname = "hoi4_typewriter16_colored"' in core
    assert 'name = "hoi4_typewriter16_colored"' in chinese
    assert '"gfx/fonts/Arial_14b"' in chinese


def test_pihc3_chinese_event_font_atlas_is_owned_by_source() -> None:
    for filename in ("Arial_14b.fnt", "Arial_14b.dds", "14b.fnt", "14b.dds"):
        asset = str(FONT_ROOT / filename)
        assert exists_file(asset), f"missing persistent PIHC3 font asset: {asset}"
        assert load_bin(asset)
