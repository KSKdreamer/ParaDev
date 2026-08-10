from pathlib import Path

from heavenbase.utils import load_txt

PROJECT_ROOT = Path("projects/PIHC3")


def _module_root(family: str, object_id: str) -> Path:
    matches = tuple((PROJECT_ROOT / "src/modules" / family).glob(f"{object_id} - *"))
    assert len(matches) == 1
    return matches[0]


def test_pihc3_initial_navies_use_history_naval_oob_loader() -> None:
    """Keep initial fleets out of runtime scripted OOB loading."""
    rows = (
        ("C25", "C25_navy_1"),
        ("C44", "C44_navy_1"),
    )

    for tag, oob in rows:
        country = load_txt(str(_module_root("country_history", f"COUNTRY_HISTORY_COUNTRIES_{tag}") / f"history/countries/{tag}.txt"))
        effect = load_txt(str(_module_root("scripted_effect", f"CREATE_{tag}_NAVY_1") / "def.txt"))

        assert f'set_naval_oob = "{oob}"' in country
        assert f"load_oob = {oob}" not in effect
        assert "create_equipment_variant" in effect
