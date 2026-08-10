from __future__ import annotations

import json
from pathlib import Path

import pytest

from paradev.pdx import PDXBlock, PDXParseError, PDXScalar, SCALAR_COLOR

PDX_SAMPLE_DIR = Path("demos/assets/pdx")
PDX_SAMPLE_FILES = [
    PDX_SAMPLE_DIR / "focus_sample.txt",
    PDX_SAMPLE_DIR / "sprite_sample.gfx",
    PDX_SAMPLE_DIR / "window_sample.gui",
    PDX_SAMPLE_DIR / "sound_sample.asset",
]


def test_block_round_trips_comments_duplicates_and_dict_projection() -> None:
    source = "\ufeff# focus comment\nfocus = { id = GER_test cost = 10 cost = 20 tags = { GER FRA } }"

    block = PDXBlock.from_str(source)
    restored = PDXBlock.load(json.loads(json.dumps(block.dump())))

    assert restored.to_dict() == {
        "focus": {
            "id": "GER_test",
            "cost": 10,
            "cost__D1": 20,
            "tags": ["GER", "FRA"],
        }
    }
    assert restored[0].comments == ["# focus comment"]
    assert "# focus comment" in restored.to_str()
    assert "GER_test" in restored.to_str()


def test_clone_preserves_lossless_shape_without_sharing_nested_state() -> None:
    block = PDXBlock.from_str("# focus comment\nfocus = { id = GER_test tags = { GER FRA } }")
    block.anno["review"] = {"authors": ["Ada"]}

    cloned = block.clone()
    cloned.anno["review"]["authors"].append("Lin")
    cloned.entries[0].comments.append("# clone only")
    nested = cloned.entries[0].val
    assert isinstance(nested, PDXBlock)
    nested.entries[0].val.anno["reviewed"] = True

    original_nested = block.entries[0].val
    assert isinstance(original_nested, PDXBlock)
    assert block.dump() != cloned.dump()
    assert block.anno == {"review": {"authors": ["Ada"]}}
    assert block.entries[0].comments == ["# focus comment"]
    assert original_nested.entries[0].val.anno.get("reviewed") is None


def test_color_scalars_and_comparison_operators_are_preserved() -> None:
    block = PDXBlock.from_str("color = rgb { 242 236 99 }\npriority > 5")

    color = block["color"]
    assert isinstance(color, PDXScalar)
    assert color.type == SCALAR_COLOR
    assert block.to_dict() == {"color": "rgb { 242 236 99 }", "priority > 5": None}
    assert "priority > 5" in block.to_str()


def test_dotted_variable_values_round_trip_as_one_scalar() -> None:
    block = PDXBlock.from_str("value = @FROM.FROM\nscore = distance_to@ROOT.capital")

    assert block.to_dict() == {
        "value": "@FROM.FROM",
        "score": "distance_to@ROOT.capital",
    }
    assert block.to_str() == "value = @FROM.FROM\nscore = distance_to@ROOT.capital\n"


def test_scripted_scalar_values_round_trip_as_one_scalar() -> None:
    block = PDXBlock.from_str(
        "\n".join(
            [
                "picture = [GetHitlerHandshakeEventPicture]",
                "localization_key = [?temp_var_PRC_military_factories]",
                "days_remove = global.days_add_support?1337",
            ]
        )
    )

    assert block.to_dict() == {
        "picture": "[GetHitlerHandshakeEventPicture]",
        "localization_key": "[?temp_var_PRC_military_factories]",
        "days_remove": "global.days_add_support?1337",
    }
    assert block.to_str() == "\n".join(
        [
            "picture = [GetHitlerHandshakeEventPicture]",
            "localization_key = [?temp_var_PRC_military_factories]",
            "days_remove = global.days_add_support?1337",
            "",
        ]
    )


def test_unquoted_path_values_round_trip_as_one_scalar() -> None:
    block = PDXBlock.from_str(
        "\n".join(
            [
                "texturefile = gfx/interface/technologies/ger_basic_light_td.dds",
                "portrait = gfx//leaders//Africa//Portrait_Africa_Generic_2.dds",
            ]
        )
    )

    assert block.to_dict() == {
        "texturefile": "gfx/interface/technologies/ger_basic_light_td.dds",
        "portrait": "gfx//leaders//Africa//Portrait_Africa_Generic_2.dds",
    }
    assert block.to_str() == "\n".join(
        [
            "texturefile = gfx/interface/technologies/ger_basic_light_td.dds",
            "portrait = gfx//leaders//Africa//Portrait_Africa_Generic_2.dds",
            "",
        ]
    )


def test_array_selector_values_round_trip_as_one_scalar() -> None:
    block = PDXBlock.from_str(
        "\n".join(
            [
                "count = FROM.warlord_subjects^num",
                "state = SWE.SWE_states_to_transfers^0",
                "score = operation_types_scores^i",
                "fallback = args^0?0.1",
                "var:SWE.SWE_states_to_transfers^0 = { id = 1 }",
            ]
        )
    )

    assert block.to_dict() == {
        "count": "FROM.warlord_subjects^num",
        "state": "SWE.SWE_states_to_transfers^0",
        "score": "operation_types_scores^i",
        "fallback": "args^0?0.1",
        "var:SWE.SWE_states_to_transfers^0": {"id": 1},
    }
    assert block.to_str() == "\n".join(
        [
            "count = FROM.warlord_subjects^num",
            "state = SWE.SWE_states_to_transfers^0",
            "score = operation_types_scores^i",
            "fallback = args^0?0.1",
            "var:SWE.SWE_states_to_transfers^0 = {",
            "\tid = 1",
            "}",
            "",
        ]
    )


def test_parser_reports_structured_diagnostics_for_unclosed_blocks() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXBlock.from_str("focus = { id = GER_test")

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.unclosed_block"
    assert diagnostic.line == 1
    assert diagnostic.column == 9
    assert diagnostic.to_dict()["message"]


def test_parser_reports_structured_diagnostics_for_missing_operator_values() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXBlock.from_str("focus =")

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.missing_value"
    assert diagnostic.line == 1
    assert diagnostic.column == 7
    assert diagnostic.to_dict()["message"] == "PDX operator '=' requires a value."


def test_parser_reports_structured_diagnostics_for_unterminated_strings() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXBlock.from_str('name = "GFX_goal')

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.unterminated_string"
    assert diagnostic.line == 1
    assert diagnostic.column == 8
    assert diagnostic.to_dict()["message"] == "Unterminated PDX string."


def test_parser_reports_structured_diagnostics_for_empty_variables() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXBlock.from_str("value = @")

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.empty_variable"
    assert diagnostic.line == 1
    assert diagnostic.column == 9
    assert diagnostic.to_dict()["message"] == "PDX variable '@' requires a name."


def test_parser_reports_structured_diagnostics_for_invalid_hex_numbers() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXBlock.from_str("value = 0x")

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.invalid_hex_number"
    assert diagnostic.line == 1
    assert diagnostic.column == 9
    assert diagnostic.to_dict()["message"] == "PDX hexadecimal number requires at least one digit."


def test_parser_attaches_scalar_spans_for_downstream_diagnostics() -> None:
    block = PDXBlock.from_str("focus = {\n\tid = GER_sample\n\tprerequisite = { focus = GER_missing }\n}")
    focus = block.find("focus")
    assert isinstance(focus.val, PDXBlock)

    focus_id = focus.val.find("id")
    prerequisite = focus.val.find("prerequisite")
    assert isinstance(prerequisite.val, PDXBlock)
    prerequisite_focus = prerequisite.val.find("focus")

    assert focus_id.val.anno["span"] == {"line": 2, "column": 7}
    assert prerequisite_focus.val.anno["span"] == {"line": 3, "column": 27}


@pytest.mark.parametrize("path", PDX_SAMPLE_FILES, ids=lambda path: path.suffix)
def test_representative_pdx_samples_round_trip(path: Path, tmp_path: Path) -> None:
    block = PDXBlock.from_file(path)

    rendered = block.to_str()
    reparsed = PDXBlock.from_str(rendered)
    dumped = PDXBlock.load(json.loads(json.dumps(block.dump())))
    output_stem = tmp_path / path.stem
    block.to_file(output_stem)

    assert block.file_ext == path.suffix
    assert reparsed.to_dict() == block.to_dict()
    assert dumped.to_dict() == block.to_dict()
    assert json.loads(json.dumps(block.to_dict())) == block.to_dict()
    assert output_stem.with_suffix(path.suffix).exists()
