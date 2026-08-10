from collections.abc import Callable, Mapping, MutableSequence, Sequence
import re
from typing import Literal

import pytest

ApiSelection = Callable[..., object]
ApiTable = Mapping[str, object]
IndexCase = tuple[str, str]
MutationMode = Literal["assign", "append"]
_SELECTOR_CONFLICT_MESSAGE = "Pass only one API table selector: symbol or index_name/key."
_UNKNOWN_INDEX_MESSAGE = "unsupported API table index 'missing_index'"


def assert_api_selection_projection(
    selection: ApiSelection,
    table: ApiTable,
    *,
    symbol: str,
    index_cases: Sequence[IndexCase],
    mutation_field: str = "value",
    mutation_symbol: str | None = None,
    mutation_mode: MutationMode = "assign",
) -> None:
    rows_by_symbol = {str(row["symbol"]): row for row in table["rows"]}

    assert selection() == table
    assert selection(symbol=symbol) == rows_by_symbol[symbol]
    for index_name, key in index_cases:
        index = table[index_name]
        assert isinstance(index, Mapping)
        assert selection(index_name=index_name, key=key) == index[key]

    mutated_symbol = mutation_symbol or symbol
    selected = selection(symbol=mutated_symbol)
    assert isinstance(selected, dict)
    expected = rows_by_symbol[mutated_symbol][mutation_field]
    if mutation_mode == "assign":
        selected[mutation_field] = "changed"
    elif mutation_mode == "append":
        mutation_target = selected[mutation_field]
        assert isinstance(mutation_target, MutableSequence)
        expected = list(expected)
        mutation_target.append("changed")
    else:
        raise AssertionError(f"unsupported API selection mutation mode {mutation_mode!r}")

    assert selection(symbol=mutated_symbol)[mutation_field] == expected


def assert_api_selection_rejects_invalid_selectors(
    selection: ApiSelection,
    *,
    symbol: str,
    index_name: str,
    key: str,
    unknown_symbol: str = "missing_symbol",
) -> None:
    with pytest.raises(ValueError, match=_SELECTOR_CONFLICT_MESSAGE):
        selection(symbol=symbol, index_name=index_name, key=key)

    with pytest.raises(ValueError, match="index_name requires key"):
        selection(index_name=index_name)

    with pytest.raises(ValueError, match=_UNKNOWN_INDEX_MESSAGE):
        selection(index_name="missing_index", key=key)

    with pytest.raises(KeyError, match=f"unknown API table symbol '{re.escape(unknown_symbol)}'"):
        selection(symbol=unknown_symbol)
