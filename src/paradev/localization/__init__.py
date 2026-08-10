"""Localization language helpers."""

from __future__ import annotations

from .api import (
    LOCALIZATION_API_TABLE_SCHEMA,
    LocalizationApiRow,
    LocalizationApiTable,
    get_localization_api_selection,
    get_localization_api_table,
    render_localization_api_reference_markdown,
)

HOI4_LANGUAGE_ALIASES = {
    "en": "l_english",
    "english": "l_english",
    "fr": "l_french",
    "french": "l_french",
    "de": "l_german",
    "german": "l_german",
    "ru": "l_russian",
    "russian": "l_russian",
    "es": "l_spanish",
    "spanish": "l_spanish",
    "pl": "l_polish",
    "polish": "l_polish",
    "pt_br": "l_braz_por",
    "braz_por": "l_braz_por",
    "br": "l_braz_por",
    "zh": "l_simp_chinese",
    "zh_cn": "l_simp_chinese",
    "simp_chinese": "l_simp_chinese",
    "ja": "l_japanese",
    "jp": "l_japanese",
    "japanese": "l_japanese",
    "ko": "l_korean",
    "kr": "l_korean",
    "korean": "l_korean",
}


def canonical_language(value: object) -> str:
    """Return the canonical HOI4 language id for a source language key.

    Args:
        value: Source language key, such as `en`, `fr`, or `l_english`.

    Returns:
        Canonical HOI4 language id when the key is a known alias; otherwise the
        normalized text value.
    """

    text = str(value).strip()
    normalized = text.lower().replace("-", "_")
    return HOI4_LANGUAGE_ALIASES.get(normalized, normalized)


__all__ = [
    "HOI4_LANGUAGE_ALIASES",
    "canonical_language",
    "LOCALIZATION_API_TABLE_SCHEMA",
    "LocalizationApiRow",
    "LocalizationApiTable",
    "get_localization_api_selection",
    "get_localization_api_table",
    "render_localization_api_reference_markdown",
]
