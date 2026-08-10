from __future__ import annotations

import pytest

from paradev.pdx import PDXParseError
from paradev.pdx.token import PDXTokenizer, TokenType, reconstruct


def test_tokenizer_handles_bom_comments_operators_and_spans() -> None:
    tokens = PDXTokenizer("\ufefffocus = { id = GER_test cost >= 10 # inline\n}").tokenize()
    typed = [token.type for token in tokens if token.type is not TokenType.EOF]

    assert typed == [
        TokenType.IDENTIFIER,
        TokenType.EQUALS,
        TokenType.LBRACE,
        TokenType.IDENTIFIER,
        TokenType.EQUALS,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.GE,
        TokenType.NUMBER,
        TokenType.COMMENT,
        TokenType.RBRACE,
    ]
    assert tokens[0].line == 1
    assert tokens[0].column == 1
    assert tokens[9].value == "# inline"


def test_token_to_dict_returns_json_safe_source_span() -> None:
    token = PDXTokenizer("focus = { id = GER_test }").tokenize()[0]

    assert token.to_dict() == {
        "type": "identifier",
        "value": "focus",
        "line": 1,
        "column": 1,
    }


def test_token_reconstruct_preserves_token_meaning() -> None:
    source = 'spriteType = { name = "GFX_goal" texturefile = "gfx\\\\goal.dds" }'
    first = PDXTokenizer(source).tokenize()
    second = PDXTokenizer(reconstruct(first)).tokenize()

    assert [(token.type, token.value) for token in second] == [(token.type, token.value) for token in first]


def test_tokenizer_keeps_dotted_variable_references_together() -> None:
    tokens = PDXTokenizer("value = @FROM.FROM\nscore = distance_to@ROOT.capital").tokenize()

    assert [(token.type, token.value) for token in tokens] == [
        (TokenType.IDENTIFIER, "value"),
        (TokenType.EQUALS, "="),
        (TokenType.VARIABLE, "@FROM.FROM"),
        (TokenType.IDENTIFIER, "score"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "distance_to@ROOT.capital"),
        (TokenType.EOF, None),
    ]


def test_tokenizer_keeps_scripted_scalar_values_together() -> None:
    tokens = PDXTokenizer(
        "\n".join(
            [
                "picture = [GetHitlerHandshakeEventPicture]",
                "localization_key = [?temp_var_PRC_military_factories]",
                "days_remove = global.days_add_support?1337",
            ]
        )
    ).tokenize()

    assert [(token.type, token.value) for token in tokens] == [
        (TokenType.IDENTIFIER, "picture"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "[GetHitlerHandshakeEventPicture]"),
        (TokenType.IDENTIFIER, "localization_key"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "[?temp_var_PRC_military_factories]"),
        (TokenType.IDENTIFIER, "days_remove"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "global.days_add_support?1337"),
        (TokenType.EOF, None),
    ]


def test_tokenizer_keeps_unquoted_path_values_together() -> None:
    tokens = PDXTokenizer(
        "\n".join(
            [
                "texturefile = gfx/interface/technologies/ger_basic_light_td.dds",
                "portrait = gfx//leaders//Africa//Portrait_Africa_Generic_2.dds",
            ]
        )
    ).tokenize()

    assert [(token.type, token.value) for token in tokens] == [
        (TokenType.IDENTIFIER, "texturefile"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "gfx/interface/technologies/ger_basic_light_td.dds"),
        (TokenType.IDENTIFIER, "portrait"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "gfx//leaders//Africa//Portrait_Africa_Generic_2.dds"),
        (TokenType.EOF, None),
    ]


def test_tokenizer_keeps_array_selector_values_together() -> None:
    tokens = PDXTokenizer(
        "\n".join(
            [
                "count = FROM.warlord_subjects^num",
                "state = SWE.SWE_states_to_transfers^0",
                "score = operation_types_scores^i",
                "fallback = args^0?0.1",
                "var:SWE.SWE_states_to_transfers^0 = { id = 1 }",
            ]
        )
    ).tokenize()

    assert [(token.type, token.value) for token in tokens] == [
        (TokenType.IDENTIFIER, "count"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "FROM.warlord_subjects^num"),
        (TokenType.IDENTIFIER, "state"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "SWE.SWE_states_to_transfers^0"),
        (TokenType.IDENTIFIER, "score"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "operation_types_scores^i"),
        (TokenType.IDENTIFIER, "fallback"),
        (TokenType.EQUALS, "="),
        (TokenType.IDENTIFIER, "args^0?0.1"),
        (TokenType.IDENTIFIER, "var:SWE.SWE_states_to_transfers^0"),
        (TokenType.EQUALS, "="),
        (TokenType.LBRACE, "{"),
        (TokenType.IDENTIFIER, "id"),
        (TokenType.EQUALS, "="),
        (TokenType.NUMBER, "1"),
        (TokenType.RBRACE, "}"),
        (TokenType.EOF, None),
    ]


def test_tokenizer_reports_unterminated_string_diagnostics() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXTokenizer('name = "GFX_goal').tokenize()

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.unterminated_string"
    assert diagnostic.line == 1
    assert diagnostic.column == 8
    assert diagnostic.to_dict()["message"] == "Unterminated PDX string."


def test_tokenizer_reports_unterminated_bracket_value_diagnostics() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXTokenizer("picture = [GetHitlerHandshakeEventPicture").tokenize()

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.unterminated_bracket_value"
    assert diagnostic.line == 1
    assert diagnostic.column == 11
    assert diagnostic.to_dict()["message"] == "Unterminated PDX bracketed value."


def test_tokenizer_reports_empty_variable_diagnostics() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXTokenizer("@").tokenize()

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.empty_variable"
    assert diagnostic.line == 1
    assert diagnostic.column == 1
    assert diagnostic.to_dict()["message"] == "PDX variable '@' requires a name."


def test_tokenizer_reports_invalid_hex_number_diagnostics() -> None:
    with pytest.raises(PDXParseError) as error:
        PDXTokenizer("0x").tokenize()

    diagnostic = error.value.diagnostics[0]
    assert diagnostic.code == "pdx.invalid_hex_number"
    assert diagnostic.line == 1
    assert diagnostic.column == 1
    assert diagnostic.to_dict()["message"] == "PDX hexadecimal number requires at least one digit."
