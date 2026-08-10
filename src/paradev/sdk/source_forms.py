"""Lossless source-form projection and patch-contract helpers."""

from __future__ import annotations

import math
import re
import textwrap
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass

from heavenbase.utils import dumps_json, loads_json

from paradev.build.slots import match_slot_paths
from paradev.localization._source import SourceEntry, parse_ini, parse_source
from paradev.pdx import (
    SCALAR_BOOL,
    SCALAR_ID,
    SCALAR_NUM,
    SCALAR_STR,
    PDXBlock,
    PDXEntry,
    PDXScalar,
    PDXTokenizer,
    TokenType,
    parse_pdx,
)

MAX_PDX_SOURCE_FORM_CONTROLS = 96
MAX_PDX_SOURCE_FORM_SECTIONS = 32
MAX_PDX_SOURCE_FORM_DEPTH = 12
MAX_LOC_SOURCE_FORM_CONTROLS = 96
MAX_SOURCE_FORM_QUERY_CHARS = 200

_PDX_SOURCE_FORM_HINT_FIELDS = frozenset(
    {
        "label",
        "description",
        "control",
        "columns",
        "minimum",
        "placeholder",
    }
)

_JSON_PATCH_FIELDS = frozenset({"op", "path"})
_LOC_PATCH_FIELDS = frozenset(
    {
        "op",
        "path",
        "span",
        "expected",
        "style",
        "newline",
        "source_length",
    }
)
_LOC_PATCH_PATH_FIELDS = frozenset({"language", "key", "occurrence"})
_LOC_PATCH_SPAN_FIELDS = frozenset({"start", "end"})
_PDX_PATCH_FIELDS = frozenset(
    {
        "op",
        "path",
        "span",
        "expected",
        "scalar_kind",
        "source_length",
    }
)
_PDX_LIST_PATCH_FIELDS = frozenset(
    {
        "op",
        "path",
        "span",
        "expected",
        "item_kind",
        "columns",
        "minimum",
        "layout",
        "source_length",
    }
)
_PDX_BLOCK_PATCH_FIELDS = frozenset(
    {
        "op",
        "path",
        "span",
        "expected",
        "layout",
        "source_length",
    }
)
_PDX_PATCH_PATH_FIELDS = frozenset({"key", "occurrence"})
_PDX_PATCH_SPAN_FIELDS = frozenset({"start", "end"})
_PDX_LIST_LAYOUT_FIELDS = frozenset(
    {
        "prefix",
        "column_separator",
        "row_separator",
        "suffix",
    }
)
_PDX_BLOCK_LAYOUT_FIELDS = frozenset({"prefix", "line_prefix", "suffix"})
_PDX_SCALAR_KINDS = frozenset({"boolean", "identifier", "number", "string"})
_LOC_STYLES = frozenset({"inline", "section", "yaml"})
_SAFE_PDX_IDENTIFIER = re.compile(r"^-?[A-Za-z_][A-Za-z0-9_-]*" r"(?:(?:[:@?./^]|//)[A-Za-z0-9_-]+)*(?:%{1,2})?$")
_SAFE_PDX_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")
_SAFE_PDX_INTEGER = re.compile(r"^-?\d+$")
_MAX_SAFE_JAVASCRIPT_INTEGER = 9_007_199_254_740_991


@dataclass(frozen=True, slots=True)
class _ExactToken:
    kind: TokenType
    start: int
    end: int
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class _PdxControl:
    key: str
    occurrence: int
    value: str | int | float | bool
    control: str
    scalar_kind: str
    expected: str
    start: int
    end: int
    path: tuple[dict[str, object], ...]


@dataclass(frozen=True, slots=True)
class _PdxIntegerListControl:
    key: str
    occurrence: int
    value: str
    expected: str
    start: int
    end: int
    path: tuple[dict[str, object], ...]
    columns: int
    minimum: int
    layout: dict[str, str]


@dataclass(frozen=True, slots=True)
class _PdxBlockBodyControl:
    key: str
    occurrence: int
    value: str
    expected: str
    start: int
    end: int
    path: tuple[dict[str, object], ...]
    layout: dict[str, str]


@dataclass(frozen=True, slots=True)
class _PdxSourceFormCandidate:
    """One safe PDX control retained until bounded query projection."""

    control: _PdxControl | _PdxIntegerListControl | _PdxBlockBodyControl
    control_index: int
    hint: Mapping[str, object] | None
    kind: str


def pdx_source_form(
    *,
    module_id: str,
    text: str,
    field_hints: Mapping[str, Mapping[str, object]] | None = None,
    query: str | None = None,
) -> dict[str, object] | None:
    """Project one bounded PDX document into exact-source guided controls.

    The projection exposes only scalar `=` assignments that can be resolved to
    one exact lexical token plus block bodies and integer lists explicitly
    declared by the active Registry family. Duplicate keys retain their
    zero-based occurrence at every path segment. Source offsets use UTF-16 code
    units so the desktop can apply reviewed spans without translating Python
    string indexes.

    Args:
        module_id (str): Canonical `family/object_id` module identity.
        text (str): Current unsaved PDX source text.
        field_hints (Mapping[str, Mapping[str, object]] | None): Optional
            Registry-family-owned labels, descriptions, placeholders, and
            guided control declarations keyed by exact PDX field name. The
            reserved `$module` selector addresses a block whose key equals the
            module object id; `$root` addresses every direct keyed block in the
            source document. ParaDev supplies contextual generated help for
            keys that the family does not declare.
        query (str | None): Optional bounded case-insensitive search. Matching
            one section identity or direct control returns that section's
            complete safe controls, within the ordinary form limits.

    Returns:
        dict[str, object] | None: Family-provider-shaped source form, or `None`
            when the document has no safe controls or exceeds the bounded form
            complexity limits.

    Raises:
        ValueError: If the PDX text or one projected source span is malformed.
    """

    if not isinstance(module_id, str) or not module_id.strip():
        raise ValueError("PDX source form module_id must be a non-empty string.")
    if not isinstance(text, str):
        raise ValueError("PDX source form text must be a string.")
    normalized_query = normalize_source_form_query(query)
    normalized_hints = _pdx_source_form_field_hints(field_hints)
    _family_id, separator, module_object_id = module_id.partition("/")
    module_object_id = module_object_id if separator else ""

    try:
        document = parse_pdx(text)
    except RecursionError as error:
        raise ValueError("PDX source form nesting is too deep to parse safely.") from error
    tokens = _pdx_exact_tokens(text)
    token_index: dict[tuple[int, int], list[_ExactToken]] = {}
    for token in tokens:
        if token.kind not in {TokenType.COMMENT, TokenType.EOF}:
            token_index.setdefault((token.line, token.column), []).append(token)

    utf16_offsets = _utf16_offset_table(text)
    source_length = utf16_offsets[-1]
    sections: list[dict[str, object]] = []
    shown_control_count = 0
    total_control_count = 0
    matched_control_count = 0
    section_count = 0
    stack: list[
        tuple[
            PDXBlock,
            tuple[dict[str, object], ...],
            tuple[str, ...],
            int,
        ]
    ] = [(document, (), (), 0)]
    while stack:
        block, parent_path, display_path, depth = stack.pop()
        if depth > MAX_PDX_SOURCE_FORM_DEPTH:
            return None
        candidates: list[_PdxSourceFormCandidate] = []
        child_blocks: list[
            tuple[
                PDXBlock,
                tuple[dict[str, object], ...],
                tuple[str, ...],
                int,
            ]
        ] = []
        occurrences: dict[str, int] = {}
        for entry in block.entries:
            segment = _pdx_entry_path_segment(entry, occurrences, text, token_index)
            if segment is None:
                continue
            path = (*parent_path, segment)
            key = str(segment["key"])
            hint = normalized_hints.get(key)
            if hint is None and key == module_object_id:
                hint = normalized_hints.get("$module")
            if hint is None and not parent_path:
                hint = normalized_hints.get("$root")
            if entry.op == "=" and isinstance(entry.val, PDXBlock):
                block_control = _pdx_block_body_control(
                    entry,
                    path,
                    text,
                    tokens,
                    token_index,
                    hint=hint,
                )
                if block_control is not None:
                    control_index = total_control_count
                    total_control_count += 1
                    candidates.append(
                        _PdxSourceFormCandidate(
                            control=block_control,
                            control_index=control_index,
                            hint=hint,
                            kind="block-body",
                        )
                    )
                    continue
                list_control = _pdx_integer_list_control(
                    entry,
                    path,
                    text,
                    tokens,
                    token_index,
                    hint=hint,
                )
                if list_control is not None:
                    control_index = total_control_count
                    total_control_count += 1
                    candidates.append(
                        _PdxSourceFormCandidate(
                            control=list_control,
                            control_index=control_index,
                            hint=hint,
                            kind="integer-list",
                        )
                    )
                    continue
                child_blocks.append(
                    (
                        entry.val,
                        path,
                        (*display_path, _pdx_display_path_segment(segment, entry.val)),
                        depth + 1,
                    )
                )
                continue
            if hint is not None and hint.get("control") in {"block-text", "integer-list"}:
                raise ValueError(f"PDX {hint['control']!s} field {key!r} must target a keyed block.")
            control = _pdx_scalar_control(entry, path, text, token_index)
            if control is None:
                continue
            control_index = total_control_count
            total_control_count += 1
            candidates.append(
                _PdxSourceFormCandidate(
                    control=control,
                    control_index=control_index,
                    hint=hint,
                    kind="scalar",
                )
            )
        if candidates:
            section_index = section_count
            section_count += 1
            section_label = _pdx_display_path_label(display_path)
            matches = normalized_query is None or _pdx_source_form_section_matches(
                normalized_query,
                section_label=section_label,
                candidates=candidates,
            )
            if matches:
                matched_control_count += len(candidates)
                remaining = MAX_PDX_SOURCE_FORM_CONTROLS - shown_control_count
                if len(sections) < MAX_PDX_SOURCE_FORM_SECTIONS and remaining > 0:
                    selected = candidates[:remaining]
                    sections.append(
                        {
                            "id": f"pdx-section-{section_index:03d}",
                            "label": section_label,
                            "controls": [
                                _pdx_source_form_candidate_control(
                                    candidate,
                                    utf16_offsets=utf16_offsets,
                                    source_length=source_length,
                                )
                                for candidate in selected
                            ],
                        }
                    )
                    shown_control_count += len(selected)
        stack.extend(reversed(child_blocks))

    if total_control_count == 0:
        return None
    coverage_total = total_control_count if normalized_query is None else matched_control_count
    return {
        "contract": "paradev.pdx.guided-form.v1",
        "label": {
            "default": "Guided PDX fields",
            "zh": "引导式 PDX 字段",
        },
        "description": {
            "default": "Edit existing simple values and Registry-supported script blocks and lists.",
            "zh": "编辑现有简单值，以及 Registry 支持的脚本块和列表。",
        },
        "coverage": {
            "truncated": shown_control_count < coverage_total,
            "shown_controls": shown_control_count,
            "total_controls": coverage_total,
        },
        **({"query": normalized_query} if normalized_query is not None else {}),
        "sections": sections,
    }


def loc_text_source_form(
    *,
    module_id: str,
    text: str,
    query: str | None = None,
) -> dict[str, object] | None:
    """Project one localization source into lossless text controls.

    Args:
        module_id (str): Canonical `family/object_id` module identity.
        text (str): Current unsaved `.loc` source text.
        query (str | None): Optional bounded case-insensitive search across
            localization language, key, and current text.

    Returns:
        dict[str, object] | None: Bounded exact-span localization form, or
            `None` when the source contains no localization entries.

    Raises:
        ValueError: If the source shape or line endings are malformed.
    """

    if not isinstance(module_id, str) or not module_id.strip():
        raise ValueError("Localization source form module_id must be a non-empty string.")
    if not isinstance(text, str):
        raise ValueError("Localization source form text must be a string.")
    normalized_query = normalize_source_form_query(query)
    document = parse_source(text)
    if document.issues:
        issue = document.issues[0]
        raise ValueError(f"Localization source line {issue.line} is invalid: " f"{issue.code.replace('_', ' ')}.")
    if not document.entries:
        return None

    utf16_offsets = _utf16_offset_table(text)
    source_length = utf16_offsets[-1]
    controls_by_language: dict[str, list[dict[str, object]]] = {}
    matched_entries = [
        (index, entry)
        for index, entry in enumerate(document.entries)
        if normalized_query is None
        or _source_form_query_matches(
            normalized_query,
            entry.language,
            entry.key,
            entry.text,
        )
    ]
    for index, entry in matched_entries[:MAX_LOC_SOURCE_FORM_CONTROLS]:
        controls_by_language.setdefault(entry.language, []).append(
            _loc_source_form_control(
                entry,
                control_index=index,
                utf16_offsets=utf16_offsets,
                source_length=source_length,
                newline=document.newline,
            )
        )
    shown = min(len(matched_entries), MAX_LOC_SOURCE_FORM_CONTROLS)
    sections = [
        {
            "id": f"loc-language-{index:03d}",
            "label": _loc_language_label(language),
            "controls": controls,
        }
        for index, (language, controls) in enumerate(controls_by_language.items())
    ]
    return {
        "contract": "paradev.localization.text-form.v1",
        "label": {
            "default": "Localization text",
            "zh": "本地化文本",
        },
        "description": {
            "default": "Edit existing translated text while ParaDev preserves keys, sections, and surrounding source text.",
            "zh": "编辑现有译文；ParaDev 会保留键、分节与周边源文本。",
        },
        "coverage": {
            "truncated": shown < len(matched_entries),
            "shown_controls": shown,
            "total_controls": len(matched_entries),
        },
        **({"query": normalized_query} if normalized_query is not None else {}),
        "sections": sections,
    }


def is_pdx_form_source(family: object, relative_path: str) -> bool:
    """Return whether a family owns one canonical PDX source path.

    Args:
        family (object): Registered build family with optional `source_slots`.
        relative_path (str): POSIX path relative to one module root.

    Returns:
        bool: `True` when the path matches a Registry-declared PDX source
            slot. Exact paths, globs, and regular expressions all use the same
            matching rules as source discovery.
    """

    return _is_source_form_slot(family, relative_path, kind="pdx")


def is_loc_text_form_source(family: object, relative_path: str) -> bool:
    """Return whether a family owns one canonical localization source path.

    Args:
        family (object): Registered build family with optional `source_slots`.
        relative_path (str): POSIX path relative to one module root.

    Returns:
        bool: `True` when the path matches a Registry-declared localization
            source slot.
    """

    return _is_source_form_slot(family, relative_path, kind="loc")


def _is_source_form_slot(family: object, relative_path: str, *, kind: str) -> bool:
    if not isinstance(relative_path, str) or not relative_path or "\\" in relative_path:
        return False
    source_slots = getattr(family, "source_slots", ())
    if not isinstance(source_slots, tuple):
        return False
    for slot in source_slots:
        if getattr(slot, "kind", None) != kind:
            continue
        matched = match_slot_paths((relative_path,), (slot,))
        if any(relative_path in paths for paths in matched.source_slots.values()):
            return True
    return False


def normalize_source_form_patch(value: object, label: str) -> dict[str, object]:
    """Validate one discriminated exact-source patch description.

    Args:
        value (object): Decoded patch mapping.
        label (str): Context label included in validation errors.

    Returns:
        dict[str, object]: Normalized JSON-safe JSON, localization, or PDX
            patch.

    Raises:
        ValueError: If the operation or any operation-specific field is invalid.
    """

    patch = _required_mapping(value, label)
    operation = _required_string(patch.get("op"), f"{label}.op")
    if operation == "replace-json-scalar":
        _validate_fields(patch, _JSON_PATCH_FIELDS, label)
        return {
            "op": operation,
            "path": _json_patch_path(patch.get("path"), f"{label}.path"),
        }
    if operation == "replace-loc-text":
        _validate_fields(patch, _LOC_PATCH_FIELDS, label)
        return _normalize_loc_patch(patch, label)
    if operation == "replace-pdx-scalar":
        _validate_fields(patch, _PDX_PATCH_FIELDS, label)
        return _normalize_pdx_patch(patch, label)
    if operation == "replace-pdx-integer-list":
        _validate_fields(patch, _PDX_LIST_PATCH_FIELDS, label)
        return _normalize_pdx_integer_list_patch(patch, label)
    if operation == "replace-pdx-block-body":
        _validate_fields(patch, _PDX_BLOCK_PATCH_FIELDS, label)
        return _normalize_pdx_block_body_patch(patch, label)
    raise ValueError(
        f"{label}.op must be 'replace-json-scalar', 'replace-loc-text', " "'replace-pdx-scalar', 'replace-pdx-integer-list', or " "'replace-pdx-block-body'."
    )


def source_form_patch_operations(
    sections: Sequence[Mapping[str, object]],
) -> frozenset[str]:
    """Return editable patch operations used by normalized form sections.

    Args:
        sections (Sequence[Mapping[str, object]]): Normalized source-form
            section tree.

    Returns:
        frozenset[str]: Distinct patch operation discriminants.
    """

    operations: set[str] = set()
    stack = list(sections)
    while stack:
        section = stack.pop()
        controls = section.get("controls")
        if isinstance(controls, list):
            for control in controls:
                if not isinstance(control, Mapping):
                    continue
                patch = control.get("patch")
                if isinstance(patch, Mapping) and isinstance(patch.get("op"), str):
                    operations.add(patch["op"])
        children = section.get("sections")
        if isinstance(children, list):
            stack.extend(child for child in children if isinstance(child, Mapping))
    return frozenset(operations)


def apply_source_form_values(
    *,
    text: str,
    source_format: str,
    sections: Sequence[Mapping[str, object]],
    values: Mapping[str, object],
) -> tuple[str, tuple[dict[str, object], ...]]:
    """Apply reviewed guided-control values to one in-memory source draft.

    The caller must pass normalized sections returned by ``Project.source_form``.
    JSON updates use provider-owned paths and emit HeavenBase's deterministic
    JSON representation. Localization and PDX updates validate every exact
    UTF-16 source span before applying non-overlapping replacements from right
    to left.

    Args:
        text: Current source text used to prepare the guided form.
        source_format: ``json``, ``loc``, or ``pdx``.
        sections: Normalized source-form sections.
        values: Mapping of editable control ids to replacement scalars.

    Returns:
        Updated full source text and deterministic change records.

    Raises:
        ValueError: If a control, value, patch, source token, or path is invalid.
    """

    if not isinstance(text, str):
        raise ValueError("Source-form update text must be a string.")
    if source_format not in {"json", "loc", "pdx"}:
        raise ValueError("Source-form update format must be 'json', 'loc', or 'pdx'.")
    if not isinstance(values, Mapping) or not values:
        raise ValueError("Source-form update values must be a non-empty object.")
    controls = _source_form_editable_controls(sections)
    requested: list[tuple[str, Mapping[str, object], str | int | float | bool]] = []
    for control_id in sorted(values):
        if not isinstance(control_id, str) or not control_id.strip():
            raise ValueError("Source-form update control ids must be non-empty strings.")
        control = controls.get(control_id)
        if control is None:
            raise ValueError(f"Source-form update references unknown or readonly control {control_id!r}.")
        replacement = _source_form_update_scalar(
            values[control_id],
            f"values.{control_id}",
        )
        _validate_source_form_control_replacement(
            control,
            replacement,
            control_id=control_id,
        )
        requested.append((control_id, control, replacement))
    if source_format == "json":
        return _apply_json_source_form_values(text, requested)
    if source_format == "loc":
        return _apply_loc_source_form_values(text, requested)
    return _apply_pdx_source_form_values(text, requested)


def _source_form_editable_controls(
    sections: Sequence[Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    controls: dict[str, Mapping[str, object]] = {}
    stack = list(sections)
    while stack:
        section = stack.pop()
        for control in section.get("controls", ()):
            if not isinstance(control, Mapping):
                raise ValueError("Source-form sections contain a malformed control.")
            control_id = control.get("id")
            patch = control.get("patch")
            if isinstance(control_id, str) and isinstance(patch, Mapping):
                controls[control_id] = control
        children = section.get("sections", ())
        if isinstance(children, Sequence) and not isinstance(children, (str, bytes)):
            stack.extend(child for child in children if isinstance(child, Mapping))
    return controls


def _apply_json_source_form_values(
    text: str,
    requested: Sequence[tuple[str, Mapping[str, object], str | int | float | bool]],
) -> tuple[str, tuple[dict[str, object], ...]]:
    try:
        document = loads_json(text, restore=False)
    except Exception as error:
        raise ValueError(f"Source-form JSON text is invalid: {error}") from error
    changes: list[dict[str, object]] = []
    seen_paths: set[tuple[str | int, ...]] = set()
    for control_id, control, replacement in requested:
        patch = normalize_source_form_patch(control["patch"], f"control {control_id!r} patch")
        if patch["op"] != "replace-json-scalar":
            raise ValueError(f"JSON control {control_id!r} must use a JSON scalar patch.")
        path = tuple(patch["path"])
        if path in seen_paths:
            raise ValueError(f"Source-form update repeats JSON path for control {control_id!r}.")
        seen_paths.add(path)
        parent, segment, previous = _json_source_form_target(document, path)
        _validate_source_form_replacement(previous, replacement, control_id)
        if _same_source_form_scalar(previous, replacement):
            continue
        if isinstance(parent, MutableMapping):
            parent[segment] = replacement
        else:
            parent[int(segment)] = replacement
        changes.append(
            {
                "control_id": control_id,
                "previous": previous,
                "value": replacement,
            }
        )
    if not changes:
        return text, ()
    rendered = dumps_json(document)
    if text.endswith("\n") and not rendered.endswith("\n"):
        rendered += "\n"
    return rendered, tuple(changes)


def _json_source_form_target(
    document: object,
    path: tuple[str | int, ...],
) -> tuple[MutableMapping[object, object] | list[object], str | int, object]:
    current = document
    for index, segment in enumerate(path):
        final = index == len(path) - 1
        if isinstance(current, MutableMapping) and isinstance(segment, str):
            if segment not in current:
                raise ValueError(f"Source-form JSON path does not exist: {list(path)!r}.")
            if final:
                return current, segment, current[segment]
            current = current[segment]
            continue
        if isinstance(current, list) and type(segment) is int:
            if segment < 0 or segment >= len(current):
                raise ValueError(f"Source-form JSON path does not exist: {list(path)!r}.")
            if final:
                return current, segment, current[segment]
            current = current[segment]
            continue
        raise ValueError(f"Source-form JSON path does not exist: {list(path)!r}.")
    raise ValueError("Source-form JSON patch path must not be empty.")


def _apply_loc_source_form_values(
    text: str,
    requested: Sequence[tuple[str, Mapping[str, object], str | int | float | bool]],
) -> tuple[str, tuple[dict[str, object], ...]]:
    source_length = len(text.encode("utf-16-le")) // 2
    replacements: list[tuple[int, int, str, str, str, str, int, str]] = []
    seen_paths: set[tuple[str, str, int]] = set()
    changes: list[dict[str, object]] = []
    for control_id, control, replacement in requested:
        patch = normalize_source_form_patch(control["patch"], f"control {control_id!r} patch")
        if patch["op"] != "replace-loc-text":
            raise ValueError(f"Localization control {control_id!r} must use a localization text patch.")
        if not isinstance(replacement, str):
            raise ValueError(f"Localization control {control_id!r} requires text.")
        if patch["source_length"] != source_length:
            raise ValueError(f"Localization control {control_id!r} source length is stale.")
        path = patch["path"]
        identity = (path["language"], path["key"], path["occurrence"])
        if identity in seen_paths:
            raise ValueError(f"Source-form update repeats localization path for control {control_id!r}.")
        seen_paths.add(identity)
        span = patch["span"]
        start = _python_index_for_utf16_offset(text, span["start"])
        end = _python_index_for_utf16_offset(text, span["end"])
        expected = patch["expected"]
        if text[start:end] != expected:
            raise ValueError(f"Localization control {control_id!r} source text is stale.")
        previous_value = control.get("value")
        if not isinstance(previous_value, str):
            raise ValueError(f"Localization control {control_id!r} has an invalid source value.")
        previous = previous_value
        normalized = _validated_loc_replacement(replacement, style=patch["style"])
        if previous == normalized:
            continue
        encoded = _quoted_loc_yaml_value(normalized) if patch["style"] == "yaml" else normalized.replace("\n", patch["newline"])
        if patch["style"] == "section" and start == end and normalized and end < len(text) and text[end] == "[":
            encoded += patch["newline"]
        replacements.append(
            (
                span["start"],
                span["end"],
                encoded,
                control_id,
                *identity,
                normalized,
            )
        )
        changes.append(
            {
                "control_id": control_id,
                "previous": previous,
                "value": normalized,
            }
        )

    ordered = sorted(replacements, key=lambda row: (row[0], row[1]))
    for previous, current in zip(ordered, ordered[1:]):
        if current[0] < previous[1]:
            raise ValueError("Source-form localization patches must not overlap.")
    updated = text
    for start_utf16, end_utf16, encoded, *_rest in reversed(ordered):
        start = _python_index_for_utf16_offset(updated, start_utf16)
        end = _python_index_for_utf16_offset(updated, end_utf16)
        updated = updated[:start] + encoded + updated[end:]
    if changes:
        _validate_loc_source_form_result(updated, replacements)
    return updated, tuple(changes)


def _validated_loc_replacement(value: str, *, style: object) -> str:
    if "\r" in value:
        raise ValueError("Localization replacements must use LF line endings.")
    if value != value.strip():
        raise ValueError("Localization replacements must not start or end with whitespace.")
    if style in {"inline", "yaml"}:
        if "\n" in value:
            raise ValueError(f"{str(style).capitalize()} localization replacements must stay on one line.")
        return value
    if style != "section":
        raise ValueError("Localization replacement style is unsupported.")
    probe = f"[en.PARADEV_VALUE]\n{value}\n[en.PARADEV_SENTINEL]\nvalue\n"
    document = parse_ini(probe)
    if document.issues or [entry.key for entry in document.entries] != [
        "PARADEV_VALUE",
        "PARADEV_SENTINEL",
    ]:
        raise ValueError("Localization replacement contains a source section header.")
    if document.entries[0].text != value:
        raise ValueError("Localization replacement changes meaning when parsed.")
    return value


def _normalized_loc_replacement(value: str) -> str:
    return "\n".join(value.splitlines())


def _quoted_loc_yaml_value(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _validate_loc_source_form_result(
    text: str,
    replacements: Sequence[tuple[int, int, str, str, str, str, int, str]],
) -> None:
    document = parse_source(text)
    if document.issues:
        raise ValueError("Localization source-form update produced invalid source syntax.")
    values = {(entry.language, entry.key, entry.occurrence): entry.text for entry in document.entries}
    expected = {
        (language, key, occurrence): value
        for (
            _start,
            _end,
            _encoded,
            _control_id,
            language,
            key,
            occurrence,
            value,
        ) in replacements
    }
    if any(values.get(identity) != value for identity, value in expected.items()):
        raise ValueError("Localization source-form update changed a different entry than requested.")


def _apply_pdx_source_form_values(
    text: str,
    requested: Sequence[tuple[str, Mapping[str, object], str | int | float | bool]],
) -> tuple[str, tuple[dict[str, object], ...]]:
    source_length = len(text.encode("utf-16-le")) // 2
    replacements: list[tuple[int, int, str, str, object, object]] = []
    for control_id, control, replacement in requested:
        patch = normalize_source_form_patch(control["patch"], f"control {control_id!r} patch")
        if patch["op"] not in {
            "replace-pdx-scalar",
            "replace-pdx-integer-list",
            "replace-pdx-block-body",
        }:
            raise ValueError(f"PDX control {control_id!r} must use a PDX patch.")
        if patch["source_length"] != source_length:
            raise ValueError(f"PDX control {control_id!r} source length is stale.")
        span = patch["span"]
        start = _python_index_for_utf16_offset(text, span["start"])
        end = _python_index_for_utf16_offset(text, span["end"])
        expected = patch["expected"]
        if text[start:end] != expected:
            raise ValueError(f"PDX control {control_id!r} source text is stale.")
        if patch["op"] == "replace-pdx-scalar":
            previous = _decode_pdx_source_form_scalar(expected, patch["scalar_kind"])
            _validate_source_form_replacement(previous, replacement, control_id)
            encoded = _encode_pdx_source_form_scalar(replacement, patch["scalar_kind"])
            if expected == encoded:
                continue
            normalized_replacement = replacement
        elif patch["op"] == "replace-pdx-integer-list":
            if not isinstance(replacement, str):
                raise ValueError(f"PDX integer-list control {control_id!r} requires text.")
            previous = _normalized_pdx_integer_list(
                expected,
                columns=patch["columns"],
                minimum=patch["minimum"],
                label=f"PDX integer-list control {control_id!r}",
            )
            normalized_replacement = _normalized_pdx_integer_list(
                replacement,
                columns=patch["columns"],
                minimum=patch["minimum"],
                label=f"PDX integer-list control {control_id!r}",
            )
            if previous == normalized_replacement:
                continue
            encoded = _encode_pdx_integer_list(
                normalized_replacement,
                layout=patch["layout"],
            )
        else:
            if not isinstance(replacement, str):
                raise ValueError(f"PDX block-body control {control_id!r} requires text.")
            actual_start, actual_end = _pdx_block_body_span(text, patch["path"])
            if (start, end) != (actual_start, actual_end):
                raise ValueError(f"PDX block-body control {control_id!r} path or span is stale.")
            previous = _normalized_pdx_block_body(
                expected,
                label=f"PDX block-body control {control_id!r} source",
            )
            normalized_replacement = _normalized_pdx_block_body(
                replacement,
                label=f"PDX block-body control {control_id!r}",
            )
            if previous == normalized_replacement:
                continue
            encoded = _encode_pdx_block_body(
                normalized_replacement,
                layout=patch["layout"],
            )
        replacements.append(
            (
                start,
                end,
                encoded,
                control_id,
                previous,
                normalized_replacement,
            )
        )
    ordered = sorted(replacements, key=lambda row: (row[0], row[1]))
    for previous, current in zip(ordered, ordered[1:]):
        if current[0] < previous[1]:
            raise ValueError("Source-form PDX patches must not overlap.")
    updated = text
    for start, end, encoded, _control_id, _previous, _replacement in reversed(ordered):
        updated = updated[:start] + encoded + updated[end:]
    if replacements:
        try:
            parse_pdx(updated)
        except (RecursionError, ValueError) as error:
            raise ValueError("PDX source-form update produced invalid source syntax.") from error
    changes = tuple(
        {
            "control_id": control_id,
            "previous": previous,
            "value": replacement,
        }
        for _start, _end, _encoded, control_id, previous, replacement in replacements
    )
    return updated, changes


def _python_index_for_utf16_offset(text: str, offset: object) -> int:
    if type(offset) is not int or offset < 0:
        raise ValueError("Exact source-form UTF-16 offset must be a non-negative integer.")
    units = 0
    for index, character in enumerate(text):
        if units == offset:
            return index
        units += 2 if ord(character) > 0xFFFF else 1
        if units > offset:
            break
    if units == offset:
        return len(text)
    raise ValueError("Exact source-form UTF-16 offset is not a source boundary.")


def _decode_pdx_source_form_scalar(token: str, scalar_kind: object) -> object:
    if scalar_kind == "boolean":
        if token not in {"yes", "no"}:
            raise ValueError("PDX boolean source token must be yes or no.")
        return token == "yes"
    if scalar_kind == "number":
        if _SAFE_PDX_NUMBER.fullmatch(token) is None:
            raise ValueError("PDX number source token is not safely editable.")
        return float(token) if "." in token else int(token)
    if scalar_kind == "identifier":
        if _SAFE_PDX_IDENTIFIER.fullmatch(token) is None:
            raise ValueError("PDX identifier source token is not safely editable.")
        return token
    if scalar_kind == "string":
        if len(token) < 2 or token[0] != '"' or token[-1] != '"':
            raise ValueError("PDX string source token must be quoted.")
        value: list[str] = []
        index = 1
        while index < len(token) - 1:
            character = token[index]
            if character == "\\":
                index += 1
                if index >= len(token) - 1:
                    raise ValueError("PDX string source token ends with an escape.")
                character = token[index]
            elif character == '"':
                raise ValueError("PDX string source token contains an unescaped quote.")
            value.append(character)
            index += 1
        return "".join(value)
    raise ValueError("PDX source-form scalar kind is unsupported.")


def _encode_pdx_source_form_scalar(value: object, scalar_kind: object) -> str:
    if scalar_kind == "boolean":
        if not isinstance(value, bool):
            raise ValueError("PDX boolean replacement must be a boolean.")
        return "yes" if value else "no"
    if scalar_kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("PDX number replacement must be a number.")
        token = str(value)
        if _SAFE_PDX_NUMBER.fullmatch(token) is None:
            raise ValueError("PDX number replacement must be a finite decimal without an exponent.")
        return token
    if not isinstance(value, str):
        raise ValueError("PDX text replacement must be a string.")
    if scalar_kind == "identifier":
        if _SAFE_PDX_IDENTIFIER.fullmatch(value) is None:
            raise ValueError("PDX identifier replacement contains unsafe syntax.")
        return value
    if scalar_kind == "string":
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    raise ValueError("PDX source-form scalar kind is unsupported.")


def _normalize_pdx_integer_token(
    token: str,
    *,
    minimum: int,
    label: str,
) -> str:
    if _SAFE_PDX_INTEGER.fullmatch(token) is None:
        raise ValueError(f"{label} contains a value that is not a decimal integer: {token!r}.")
    value = int(token)
    if abs(value) > _MAX_SAFE_JAVASCRIPT_INTEGER:
        raise ValueError(f"{label} contains an integer outside JavaScript's safe range.")
    if value < minimum:
        raise ValueError(f"{label} contains {value}, below the minimum {minimum}.")
    return str(value)


def _normalized_pdx_integer_list(
    value: str,
    *,
    columns: int,
    minimum: int,
    label: str,
) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    tokens = [
        _normalize_pdx_integer_token(
            token,
            minimum=minimum,
            label=label,
        )
        for token in value.split()
    ]
    if not tokens:
        raise ValueError(f"{label} must contain at least one integer.")
    if len(tokens) % columns:
        raise ValueError(f"{label} must contain exactly {columns} integers per row.")
    return "\n".join(" ".join(tokens[index : index + columns]) for index in range(0, len(tokens), columns))


def _encode_pdx_integer_list(
    value: str,
    *,
    layout: Mapping[str, object],
) -> str:
    rows = value.splitlines()
    column_separator = str(layout["column_separator"])
    row_separator = str(layout["row_separator"])
    rendered_rows = [column_separator.join(row.split()) for row in rows]
    return str(layout["prefix"]) + row_separator.join(rendered_rows) + str(layout["suffix"])


def _normalized_pdx_block_body(value: str, *, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    normalized = value.replace("\r\n", "\n")
    if "\r" in normalized:
        raise ValueError(f"{label} contains unsupported line endings.")
    normalized = textwrap.dedent(normalized).strip(" \t\n")
    probe = f"PARADEV_BLOCK = {{\n{normalized}\n}}\n"
    try:
        document = parse_pdx(probe)
    except (RecursionError, ValueError) as error:
        raise ValueError(f"{label} contains invalid PDX block syntax.") from error
    if len(document.entries) != 1 or not isinstance(document.entries[0].val, PDXBlock):
        raise ValueError(f"{label} must remain inside one PDX block.")
    tokens = tuple(token for token in _pdx_exact_tokens(probe) if token.kind not in {TokenType.COMMENT, TokenType.EOF})
    if not tokens or tokens[-1].kind is not TokenType.RBRACE:
        raise ValueError(f"{label} must not close its containing PDX block.")
    return normalized


def _encode_pdx_block_body(
    value: str,
    *,
    layout: Mapping[str, object],
) -> str:
    suffix = str(layout["suffix"])
    if not value:
        return suffix
    line_prefix = str(layout["line_prefix"])
    rendered = line_prefix.join(value.splitlines())
    return str(layout["prefix"]) + rendered + suffix


def _source_form_update_scalar(
    value: object,
    label: str,
) -> str | int | float | bool:
    if isinstance(value, (str, bool)):
        return value
    if type(value) is int:
        if abs(value) > _MAX_SAFE_JAVASCRIPT_INTEGER:
            raise ValueError(f"{label} must be a JavaScript-safe integer.")
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError(f"{label} must be a finite string, number, or boolean scalar.")


def _validate_source_form_control_replacement(
    control: Mapping[str, object],
    replacement: object,
    *,
    control_id: str,
) -> None:
    control_kind = control.get("control")
    if control_kind == "text" and not isinstance(replacement, str):
        raise ValueError(f"Source-form text control {control_id!r} requires a string.")
    if control_kind == "boolean" and not isinstance(replacement, bool):
        raise ValueError(f"Source-form boolean control {control_id!r} requires a boolean.")
    if control_kind == "number":
        if isinstance(replacement, bool) or not isinstance(replacement, (int, float)):
            raise ValueError(f"Source-form number control {control_id!r} requires a number.")
        minimum = control.get("min")
        maximum = control.get("max")
        if isinstance(minimum, (int, float)) and replacement < minimum:
            raise ValueError(f"Source-form number control {control_id!r} is below its minimum.")
        if isinstance(maximum, (int, float)) and replacement > maximum:
            raise ValueError(f"Source-form number control {control_id!r} exceeds its maximum.")
    if control_kind == "choice":
        choices = control.get("choices")
        if not isinstance(choices, Sequence) or not any(
            isinstance(choice, Mapping) and _same_source_form_scalar(choice.get("value"), replacement) for choice in choices
        ):
            raise ValueError(f"Source-form choice control {control_id!r} requires one declared choice.")


def _validate_source_form_replacement(
    previous: object,
    replacement: object,
    control_id: str,
) -> None:
    if isinstance(previous, (Mapping, list)) or previous is None:
        raise ValueError(f"Source-form control {control_id!r} does not target a supported scalar.")
    if _source_form_scalar_type(previous) != _source_form_scalar_type(replacement):
        raise ValueError(f"Source-form control {control_id!r} replacement type does not match its source scalar.")


def _same_source_form_scalar(left: object, right: object) -> bool:
    return _source_form_scalar_type(left) == _source_form_scalar_type(right) and left == right


def _source_form_scalar_type(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    return "unsupported"


def _loc_source_form_control(
    entry: SourceEntry,
    *,
    control_index: int,
    utf16_offsets: Sequence[int],
    source_length: int,
    newline: str,
) -> dict[str, object]:
    occurrence = f" ({entry.occurrence + 1})" if entry.occurrence else ""
    return {
        "id": f"loc-control-{control_index:03d}",
        "label": entry.key + occurrence,
        "description": {
            "default": f"Text for {entry.key} in {entry.language}.",
            "zh": f"{entry.language} 中 {entry.key} 的文本。",
        },
        "description_source": "generated",
        "control": "text",
        "value": entry.text,
        "multiline": entry.style == "section",
        "patch": {
            "op": "replace-loc-text",
            "path": {
                "language": entry.language,
                "key": entry.key,
                "occurrence": entry.occurrence,
            },
            "span": {
                "start": utf16_offsets[entry.start],
                "end": utf16_offsets[entry.end],
            },
            "expected": entry.expected,
            "style": entry.style,
            "newline": newline,
            "source_length": source_length,
        },
    }


def _loc_language_label(language: str) -> dict[str, str]:
    names = {
        "l_english": ("English", "英语"),
        "l_simp_chinese": ("Simplified Chinese", "简体中文"),
        "l_french": ("French", "法语"),
        "l_german": ("German", "德语"),
        "l_russian": ("Russian", "俄语"),
    }
    default, chinese = names.get(language, (language, language))
    return {
        "default": f"{default} ({language})",
        "zh": f"{chinese}（{language}）",
    }


def normalize_source_form_query(value: str | None) -> str | None:
    """Normalize one optional bounded guided-form search query.

    Args:
        value (str | None): Caller-supplied query or ``None``.

    Returns:
        str | None: Trimmed query, or ``None`` for an empty query.

    Raises:
        TypeError: If ``value`` is not text or ``None``.
        ValueError: If the trimmed query exceeds the bounded transport limit.
    """

    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("Source-form query must be a string or null.")
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > MAX_SOURCE_FORM_QUERY_CHARS:
        raise ValueError(f"Source-form query must contain at most {MAX_SOURCE_FORM_QUERY_CHARS} characters.")
    return normalized


def _source_form_query_matches(query: str, *values: object) -> bool:
    tokens = tuple(part.casefold() for part in query.split() if part)
    haystack = " ".join(_source_form_search_text(value) for value in values).casefold()
    return all(token in haystack for token in tokens)


def _source_form_search_text(value: object) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{_source_form_search_text(key)} {_source_form_search_text(item)}" for key, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return " ".join(_source_form_search_text(item) for item in value)
    return str(value)


def _pdx_source_form_section_matches(
    query: str,
    *,
    section_label: str,
    candidates: Sequence[_PdxSourceFormCandidate],
) -> bool:
    if _source_form_query_matches(query, section_label):
        return True
    return any(
        _source_form_query_matches(
            query,
            section_label,
            candidate.control.key,
            candidate.control.value,
            candidate.control.path,
            candidate.hint or {},
        )
        for candidate in candidates
    )


def _pdx_source_form_candidate_control(
    candidate: _PdxSourceFormCandidate,
    *,
    utf16_offsets: Sequence[int],
    source_length: int,
) -> dict[str, object]:
    if candidate.kind == "scalar" and isinstance(candidate.control, _PdxControl):
        return _pdx_source_form_control(
            candidate.control,
            control_index=candidate.control_index,
            utf16_offsets=utf16_offsets,
            source_length=source_length,
            hint=candidate.hint,
        )
    if candidate.kind == "integer-list" and isinstance(candidate.control, _PdxIntegerListControl):
        return _pdx_integer_list_source_form_control(
            candidate.control,
            control_index=candidate.control_index,
            utf16_offsets=utf16_offsets,
            source_length=source_length,
            hint=candidate.hint,
        )
    if candidate.kind == "block-body" and isinstance(candidate.control, _PdxBlockBodyControl):
        return _pdx_block_body_source_form_control(
            candidate.control,
            control_index=candidate.control_index,
            utf16_offsets=utf16_offsets,
            source_length=source_length,
            hint=candidate.hint,
        )
    raise TypeError(f"Unsupported PDX source-form candidate kind: {candidate.kind!r}.")


def _pdx_entry_path_segment(
    entry: PDXEntry,
    occurrences: dict[str, int],
    text: str,
    token_index: Mapping[tuple[int, int], Sequence[_ExactToken]],
) -> dict[str, object] | None:
    key = entry.key
    if key is None or key.type not in {SCALAR_ID, SCALAR_STR}:
        return None
    _pdx_scalar_exact_token(key, text, token_index)
    evaluated = key.eval()
    if not isinstance(evaluated, str) or not evaluated:
        return None
    occurrence = occurrences.get(evaluated, 0)
    occurrences[evaluated] = occurrence + 1
    return {"key": evaluated, "occurrence": occurrence}


def _pdx_scalar_control(
    entry: PDXEntry,
    path: tuple[dict[str, object], ...],
    text: str,
    token_index: Mapping[tuple[int, int], Sequence[_ExactToken]],
) -> _PdxControl | None:
    if entry.op != "=" or not isinstance(entry.val, PDXScalar):
        return None
    scalar = entry.val
    classification = _pdx_scalar_value(scalar)
    if classification is None:
        return None
    value, control, scalar_kind = classification
    token = _pdx_scalar_exact_token(scalar, text, token_index)
    expected = text[token.start : token.end]
    segment = path[-1]
    return _PdxControl(
        key=str(segment["key"]),
        occurrence=int(segment["occurrence"]),
        value=value,
        control=control,
        scalar_kind=scalar_kind,
        expected=expected,
        start=token.start,
        end=token.end,
        path=path,
    )


def _pdx_integer_list_control(
    entry: PDXEntry,
    path: tuple[dict[str, object], ...],
    text: str,
    tokens: Sequence[_ExactToken],
    token_index: Mapping[tuple[int, int], Sequence[_ExactToken]],
    *,
    hint: Mapping[str, object] | None,
) -> _PdxIntegerListControl | None:
    if hint is None or hint.get("control") != "integer-list":
        return None
    if entry.op != "=" or not isinstance(entry.val, PDXBlock) or entry.key is None:
        raise ValueError("PDX integer-list hints must target keyed blocks.")
    columns = int(hint["columns"])
    minimum = int(hint["minimum"])
    item_tokens: list[_ExactToken] = []
    for item in entry.val.entries:
        if not item.is_bare or item.key is None or item.key.type != SCALAR_NUM:
            raise ValueError(f"PDX integer-list field {str(path[-1]['key'])!r} contains non-integer syntax.")
        token = _pdx_scalar_exact_token(item.key, text, token_index)
        raw = text[token.start : token.end]
        _normalize_pdx_integer_token(
            raw,
            minimum=minimum,
            label=f"PDX integer-list field {str(path[-1]['key'])!r}",
        )
        item_tokens.append(token)
    if not item_tokens:
        raise ValueError(f"PDX integer-list field {str(path[-1]['key'])!r} must contain at least one integer.")
    if entry.val.trailing_comments or any(item.comments or item.inline_comment for item in entry.val.entries):
        raise ValueError(f"PDX integer-list field {str(path[-1]['key'])!r} contains comments; edit it in Code.")

    opening, closing, interior_tokens = _pdx_block_exact_tokens(
        entry,
        text,
        tokens,
        token_index,
    )
    if any(token.kind is TokenType.COMMENT for token in interior_tokens):
        raise ValueError(f"PDX integer-list field {str(path[-1]['key'])!r} contains comments; edit it in Code.")
    if [(token.kind, token.start, token.end) for token in interior_tokens] != [(token.kind, token.start, token.end) for token in item_tokens]:
        raise ValueError(f"PDX integer-list field {str(path[-1]['key'])!r} contains unsupported tokens.")

    expected = text[opening.end : closing.start]
    value = _normalized_pdx_integer_list(
        expected,
        columns=columns,
        minimum=minimum,
        label=f"PDX integer-list field {str(path[-1]['key'])!r}",
    )
    segment = path[-1]
    return _PdxIntegerListControl(
        key=str(segment["key"]),
        occurrence=int(segment["occurrence"]),
        value=value,
        expected=expected,
        start=opening.end,
        end=closing.start,
        path=path,
        columns=columns,
        minimum=minimum,
        layout=_pdx_integer_list_layout(
            text,
            start=opening.end,
            end=closing.start,
            item_tokens=item_tokens,
        ),
    )


def _pdx_block_body_control(
    entry: PDXEntry,
    path: tuple[dict[str, object], ...],
    text: str,
    tokens: Sequence[_ExactToken],
    token_index: Mapping[tuple[int, int], Sequence[_ExactToken]],
    *,
    hint: Mapping[str, object] | None,
) -> _PdxBlockBodyControl | None:
    if hint is None or hint.get("control") != "block-text":
        return None
    if entry.op != "=" or not isinstance(entry.val, PDXBlock) or entry.key is None:
        raise ValueError("PDX block-text hints must target keyed blocks.")
    opening, closing, interior_tokens = _pdx_block_exact_tokens(
        entry,
        text,
        tokens,
        token_index,
    )
    expected = text[opening.end : closing.start]
    segment = path[-1]
    label = f"PDX block-text field {str(segment['key'])!r}"
    return _PdxBlockBodyControl(
        key=str(segment["key"]),
        occurrence=int(segment["occurrence"]),
        value=_normalized_pdx_block_body(expected, label=label),
        expected=expected,
        start=opening.end,
        end=closing.start,
        path=path,
        layout=_pdx_block_body_layout(
            text,
            opening=opening,
            closing=closing,
            interior_tokens=interior_tokens,
        ),
    )


def _pdx_block_exact_tokens(
    entry: PDXEntry,
    text: str,
    tokens: Sequence[_ExactToken],
    token_index: Mapping[tuple[int, int], Sequence[_ExactToken]],
) -> tuple[_ExactToken, _ExactToken, tuple[_ExactToken, ...]]:
    if entry.key is None:
        raise ValueError("PDX keyed block is missing its key token.")
    key_token = _pdx_scalar_exact_token(entry.key, text, token_index)
    try:
        key_index = tokens.index(key_token)
    except ValueError as error:
        raise ValueError("PDX keyed block key is missing from the lexical stream.") from error
    operator_index = key_index + 1
    opening_index = key_index + 2
    if opening_index >= len(tokens):
        raise ValueError("PDX keyed block is missing its opening brace.")
    if tokens[operator_index].kind is not TokenType.EQUALS:
        raise ValueError("PDX keyed block must use an exact equals operator.")
    opening = tokens[opening_index]
    if opening.kind is not TokenType.LBRACE:
        raise ValueError("PDX keyed block is missing its exact opening brace.")
    depth = 0
    for index in range(opening_index, len(tokens)):
        token = tokens[index]
        if token.kind is TokenType.LBRACE:
            depth += 1
        elif token.kind is TokenType.RBRACE:
            depth -= 1
            if depth == 0:
                return opening, token, tuple(tokens[opening_index + 1 : index])
    raise ValueError("PDX keyed block is missing its exact closing brace.")


def _pdx_block_body_span(
    text: str,
    path: Sequence[Mapping[str, object]],
) -> tuple[int, int]:
    try:
        block = parse_pdx(text)
    except (RecursionError, ValueError) as error:
        raise ValueError("PDX block-body source is no longer valid PDX.") from error
    selected: PDXEntry | None = None
    for path_index, segment in enumerate(path):
        key = str(segment["key"])
        occurrence = int(segment["occurrence"])
        matches: list[PDXEntry] = []
        for entry in block.entries:
            if entry.key is None or entry.key.type not in {SCALAR_ID, SCALAR_STR}:
                continue
            if entry.key.eval() == key:
                matches.append(entry)
        if occurrence >= len(matches):
            raise ValueError(f"PDX block-body path does not contain {key!r} occurrence {occurrence + 1}.")
        selected = matches[occurrence]
        if selected.op != "=" or not isinstance(selected.val, PDXBlock):
            raise ValueError(f"PDX block-body path segment {key!r} does not target a keyed block.")
        if path_index < len(path) - 1:
            block = selected.val
    if selected is None:
        raise ValueError("PDX block-body path must not be empty.")
    tokens = _pdx_exact_tokens(text)
    token_index: dict[tuple[int, int], list[_ExactToken]] = {}
    for token in tokens:
        if token.kind not in {TokenType.COMMENT, TokenType.EOF}:
            token_index.setdefault((token.line, token.column), []).append(token)
    opening, closing, _interior_tokens = _pdx_block_exact_tokens(
        selected,
        text,
        tokens,
        token_index,
    )
    return opening.end, closing.start


def _pdx_block_body_layout(
    text: str,
    *,
    opening: _ExactToken,
    closing: _ExactToken,
    interior_tokens: Sequence[_ExactToken],
) -> dict[str, str]:
    expected = text[opening.end : closing.start]
    if "\r" in expected.replace("\r\n", ""):
        raise ValueError("PDX block-text layout contains unsupported line endings.")
    newline = "\r\n" if "\r\n" in text else "\n"
    closing_line_start = text.rfind("\n", 0, closing.start) + 1
    closing_indent = text[closing_line_start : closing.start]
    if any(character not in " \t" for character in closing_indent):
        closing_indent = ""
    body_indent = ""
    if interior_tokens:
        first = interior_tokens[0]
        first_line_start = text.rfind("\n", 0, first.start) + 1
        candidate = text[first_line_start : first.start]
        if all(character in " \t" for character in candidate):
            body_indent = candidate
    if not body_indent or not body_indent.startswith(closing_indent) or body_indent == closing_indent:
        indent_unit = "\t" if "\t" in expected or "\t" in closing_indent else "    "
        body_indent = closing_indent + indent_unit
    return {
        "prefix": newline + body_indent,
        "line_prefix": newline + body_indent,
        "suffix": newline + closing_indent,
    }


def _pdx_integer_list_layout(
    text: str,
    *,
    start: int,
    end: int,
    item_tokens: Sequence[_ExactToken],
) -> dict[str, str]:
    first = item_tokens[0]
    last = item_tokens[-1]
    prefix = text[start : first.start]
    suffix = text[last.end : end]
    expected = text[start:end]
    if any(character not in " \t\r\n" for character in prefix + suffix):
        raise ValueError("PDX integer-list layout contains non-whitespace syntax.")
    if "\r" in expected.replace("\r\n", ""):
        raise ValueError("PDX integer-list layout contains unsupported line endings.")
    newline = "\r\n" if "\r\n" in expected else "\n" if "\n" in expected else ""
    if newline:
        line_start = text.rfind("\n", start, first.start) + 1
        item_indent = text[line_start : first.start]
        if any(character not in " \t" for character in item_indent):
            raise ValueError("PDX integer-list indentation is malformed.")
        row_separator = newline + item_indent
    else:
        row_separator = " "
    return {
        "prefix": prefix,
        "column_separator": " ",
        "row_separator": row_separator,
        "suffix": suffix,
    }


def _pdx_scalar_value(
    scalar: PDXScalar,
) -> tuple[str | int | float | bool, str, str] | None:
    if scalar.type == SCALAR_BOOL:
        value = scalar.eval()
        return (value, "boolean", "boolean") if isinstance(value, bool) else None
    if scalar.type == SCALAR_NUM:
        if _SAFE_PDX_NUMBER.fullmatch(scalar.raw) is None:
            return None
        value = scalar.eval()
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if not math.isfinite(value):
            return None
        if isinstance(value, int) and abs(value) > _MAX_SAFE_JAVASCRIPT_INTEGER:
            return None
        return value, "number", "number"
    if scalar.type == SCALAR_STR:
        value = scalar.eval()
        return (value, "text", "string") if isinstance(value, str) else None
    if scalar.type == SCALAR_ID:
        value = scalar.eval()
        if isinstance(value, str) and _SAFE_PDX_IDENTIFIER.fullmatch(scalar.raw) is not None:
            return value, "text", "identifier"
    return None


def _pdx_source_form_control(
    control: _PdxControl,
    *,
    control_index: int,
    utf16_offsets: Sequence[int],
    source_length: int,
    hint: Mapping[str, object] | None,
) -> dict[str, object]:
    start = utf16_offsets[control.start]
    end = utf16_offsets[control.end]
    occurrence = f" ({control.occurrence + 1})" if control.occurrence else ""
    label = _human_pdx_key(control.key) + occurrence
    description: object = _pdx_control_description(control.path)
    description_source = "generated"
    if hint is not None:
        if "label" in hint:
            label = hint["label"]
        if "description" in hint:
            description = hint["description"]
            description_source = "declared"
    return {
        "id": f"pdx-control-{control_index:03d}",
        "label": label,
        "description": description,
        "description_source": description_source,
        "control": control.control,
        "value": control.value,
        "patch": {
            "op": "replace-pdx-scalar",
            "path": [dict(segment) for segment in control.path],
            "span": {"start": start, "end": end},
            "expected": control.expected,
            "scalar_kind": control.scalar_kind,
            "source_length": source_length,
        },
    }


def _pdx_integer_list_source_form_control(
    control: _PdxIntegerListControl,
    *,
    control_index: int,
    utf16_offsets: Sequence[int],
    source_length: int,
    hint: Mapping[str, object] | None,
) -> dict[str, object]:
    start = utf16_offsets[control.start]
    end = utf16_offsets[control.end]
    occurrence = f" ({control.occurrence + 1})" if control.occurrence else ""
    label: object = _human_pdx_key(control.key) + occurrence
    description: object = _pdx_integer_list_description(
        control.path,
        columns=control.columns,
    )
    description_source = "generated"
    if hint is not None:
        if "label" in hint:
            label = hint["label"]
        if "description" in hint:
            description = hint["description"]
            description_source = "declared"
    placeholder = (
        {
            "default": "One integer per line",
            "zh": "每行一个整数",
        }
        if control.columns == 1
        else {
            "default": f"One row per {control.columns} integers",
            "zh": f"每行 {control.columns} 个整数",
        }
    )
    return {
        "id": f"pdx-control-{control_index:03d}",
        "label": label,
        "description": description,
        "description_source": description_source,
        "control": "text",
        "value": control.value,
        "multiline": True,
        "placeholder": placeholder,
        "patch": {
            "op": "replace-pdx-integer-list",
            "path": [dict(segment) for segment in control.path],
            "span": {"start": start, "end": end},
            "expected": control.expected,
            "item_kind": "integer",
            "columns": control.columns,
            "minimum": control.minimum,
            "layout": dict(control.layout),
            "source_length": source_length,
        },
    }


def _pdx_block_body_source_form_control(
    control: _PdxBlockBodyControl,
    *,
    control_index: int,
    utf16_offsets: Sequence[int],
    source_length: int,
    hint: Mapping[str, object] | None,
) -> dict[str, object]:
    start = utf16_offsets[control.start]
    end = utf16_offsets[control.end]
    occurrence = f" ({control.occurrence + 1})" if control.occurrence else ""
    label: object = _human_pdx_key(control.key) + " body" + occurrence
    description: object = _pdx_block_body_description(control.path)
    description_source = "generated"
    placeholder: object = {
        "default": "Enter PDX statements without the outer braces",
        "zh": "输入不含外层花括号的 PDX 语句",
    }
    if hint is not None:
        if "label" in hint:
            label = hint["label"]
        if "description" in hint:
            description = hint["description"]
            description_source = "declared"
        if "placeholder" in hint:
            placeholder = hint["placeholder"]
    return {
        "id": f"pdx-control-{control_index:03d}",
        "label": label,
        "description": description,
        "description_source": description_source,
        "control": "text",
        "value": control.value,
        "multiline": True,
        "placeholder": placeholder,
        "patch": {
            "op": "replace-pdx-block-body",
            "path": [dict(segment) for segment in control.path],
            "span": {"start": start, "end": end},
            "expected": control.expected,
            "layout": dict(control.layout),
            "source_length": source_length,
        },
    }


def _pdx_source_form_field_hints(
    value: Mapping[str, Mapping[str, object]] | None,
) -> dict[str, dict[str, object]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("PDX source-form field hints must be a mapping.")
    normalized: dict[str, dict[str, object]] = {}
    for raw_key, raw_hint in value.items():
        if not isinstance(raw_key, str) or not raw_key.strip():
            raise ValueError("PDX source-form field hint keys must be non-empty strings.")
        if not isinstance(raw_hint, Mapping):
            raise TypeError(f"PDX source-form field hint {raw_key!r} must be a mapping.")
        unsupported = sorted(set(raw_hint) - _PDX_SOURCE_FORM_HINT_FIELDS)
        if unsupported:
            names = ", ".join(str(field) for field in unsupported)
            raise ValueError(f"PDX source-form field hint {raw_key!r} contains unsupported fields: {names}.")
        if not raw_hint:
            raise ValueError(f"PDX source-form field hint {raw_key!r} must not be empty.")
        hint = dict(raw_hint)
        control = hint.get("control")
        list_fields = tuple(field for field in ("columns", "minimum") if field in hint)
        if control is None:
            if list_fields:
                names = ", ".join(list_fields)
                raise ValueError(f"PDX source-form field hint {raw_key!r} fields {names} require " "control='integer-list'.")
        elif control == "integer-list":
            columns = hint.get("columns", 1)
            if type(columns) is not int or columns < 1 or columns > 16:
                raise ValueError(f"PDX source-form field hint {raw_key!r}.columns must be an integer from 1 to 16.")
            minimum = hint.get("minimum", -_MAX_SAFE_JAVASCRIPT_INTEGER)
            if type(minimum) is not int or minimum < -_MAX_SAFE_JAVASCRIPT_INTEGER or minimum > _MAX_SAFE_JAVASCRIPT_INTEGER:
                raise ValueError(f"PDX source-form field hint {raw_key!r}.minimum must be a JavaScript-safe integer.")
            hint["columns"] = columns
            hint["minimum"] = minimum
        elif control == "block-text":
            if list_fields:
                names = ", ".join(list_fields)
                raise ValueError(f"PDX source-form field hint {raw_key!r} fields {names} require " "control='integer-list'.")
        else:
            raise ValueError(f"PDX source-form field hint {raw_key!r}.control must be " "'integer-list' or 'block-text'.")
        normalized[raw_key] = hint
    return normalized


def _pdx_control_description(path: Sequence[Mapping[str, object]]) -> dict[str, str]:
    path_text = " › ".join(str(segment["key"]) for segment in path)
    return {
        "default": f"Edit the existing PDX value at {path_text}.",
        "zh": f"编辑 PDX 路径 {path_text} 上的现有值。",
    }


def _pdx_integer_list_description(
    path: Sequence[Mapping[str, object]],
    *,
    columns: int,
) -> dict[str, str]:
    path_text = " › ".join(str(segment["key"]) for segment in path)
    if columns == 1:
        return {
            "default": f"Edit the integer list at {path_text}, one value per line.",
            "zh": f"编辑 PDX 路径 {path_text} 的整数列表，每行一个值。",
        }
    return {
        "default": (f"Edit the integer table at {path_text}, with {columns} values per row."),
        "zh": f"编辑 PDX 路径 {path_text} 的整数表格，每行 {columns} 个值。",
    }


def _pdx_block_body_description(path: Sequence[Mapping[str, object]]) -> dict[str, str]:
    path_text = " › ".join(str(segment["key"]) for segment in path)
    return {
        "default": f"Edit the statements inside the PDX block at {path_text}; outer braces stay managed.",
        "zh": f"编辑 PDX 路径 {path_text} 块内的语句；外层花括号由系统管理。",
    }


def _pdx_path_label(path: Sequence[Mapping[str, object]]) -> str:
    if not path:
        return "Top level"
    parts: list[str] = []
    for segment in path:
        key = str(segment["key"])
        occurrence = int(segment["occurrence"])
        parts.append(f"{key} ({occurrence + 1})" if occurrence else key)
    return " › ".join(parts)


def _pdx_display_path_segment(segment: Mapping[str, object], block: PDXBlock) -> str:
    key = str(segment["key"])
    occurrence = int(segment["occurrence"])
    label = f"{key} ({occurrence + 1})" if occurrence else key
    identity = _pdx_block_display_identity(block)
    return f"{label} — {identity}" if identity is not None else label


def _pdx_block_display_identity(block: PDXBlock) -> str | None:
    identities: dict[str, str] = {}
    for entry in block.entries:
        if entry.op != "=" or entry.key is None or not isinstance(entry.val, PDXScalar):
            continue
        key = entry.key.eval()
        if key not in {"id", "name"}:
            continue
        classified = _pdx_scalar_value(entry.val)
        if classified is None:
            continue
        value = str(classified[0]).strip()
        if value and len(value) <= 120:
            identities[str(key)] = value
    return identities.get("id") or identities.get("name")


def _pdx_display_path_label(path: Sequence[str]) -> str:
    return " › ".join(path) if path else "Top level"


def _human_pdx_key(key: str) -> str:
    words = " ".join(part for part in key.replace("_", " ").split() if part)
    return words[:1].upper() + words[1:] if words else key


def _pdx_scalar_exact_token(
    scalar: PDXScalar,
    text: str,
    token_index: Mapping[tuple[int, int], Sequence[_ExactToken]],
) -> _ExactToken:
    span = scalar.anno.get("span")
    if not isinstance(span, Mapping):
        raise ValueError("PDX scalar is missing its parser source span.")
    line = span.get("line")
    column = span.get("column")
    if not isinstance(line, int) or not isinstance(column, int):
        raise ValueError("PDX scalar parser source span is malformed.")
    matches = token_index.get((line, column), ())
    if len(matches) != 1:
        raise ValueError(f"PDX scalar at line {line}, column {column} does not resolve " "to exactly one lexical token.")
    token = matches[0]
    raw = text[token.start : token.end]
    if not scalar.raw or raw != scalar.raw:
        raise ValueError(f"PDX scalar at line {line}, column {column} does not match " "its exact source token.")
    return token


def _pdx_exact_tokens(text: str) -> tuple[_ExactToken, ...]:
    bom_offset = 1 if text.startswith("\ufeff") else 0
    visible = text[bom_offset:]
    line_starts = [0]
    line_starts.extend(index + 1 for index, character in enumerate(visible) if character == "\n")
    rows: list[_ExactToken] = []
    for token in PDXTokenizer(text).tokenize():
        if token.line < 1 or token.line > len(line_starts):
            raise ValueError(f"PDX token reports invalid source line {token.line}.")
        start = bom_offset + line_starts[token.line - 1] + token.column - 1
        end = _pdx_token_end(text, start, token.type, token.value)
        rows.append(
            _ExactToken(
                kind=token.type,
                start=start,
                end=end,
                line=token.line,
                column=token.column,
            )
        )
    return tuple(rows)


def _pdx_token_end(
    text: str,
    start: int,
    kind: TokenType,
    value: object,
) -> int:
    if kind is TokenType.EOF:
        return start
    if kind is TokenType.COMMENT:
        newline = text.find("\n", start)
        return len(text) if newline < 0 else newline
    if kind is TokenType.STRING:
        index = start + 1
        while index < len(text):
            if text[index] == "\\":
                index += 2
                continue
            if text[index] == '"':
                return index + 1
            index += 1
        raise ValueError(f"PDX string token at offset {start} is unterminated.")
    raw = str(value)
    end = start + len(raw)
    if text[start:end] != raw:
        raise ValueError(f"PDX token at offset {start} does not match its lexical value.")
    return end


def _utf16_offset_table(text: str) -> tuple[int, ...]:
    offsets = [0]
    for character in text:
        offsets.append(offsets[-1] + (2 if ord(character) > 0xFFFF else 1))
    return tuple(offsets)


def _normalize_loc_patch(
    patch: Mapping[object, object],
    label: str,
) -> dict[str, object]:
    raw_path = _required_mapping(patch.get("path"), f"{label}.path")
    _validate_fields(raw_path, _LOC_PATCH_PATH_FIELDS, f"{label}.path")
    path = {
        "language": _required_string(raw_path.get("language"), f"{label}.path.language"),
        "key": _required_string(raw_path.get("key"), f"{label}.path.key"),
        "occurrence": _non_negative_int(
            raw_path.get("occurrence"),
            f"{label}.path.occurrence",
        ),
    }
    if not path["language"].startswith("l_"):
        raise ValueError(f"{label}.path.language must be a canonical localization language.")

    span = _required_mapping(patch.get("span"), f"{label}.span")
    _validate_fields(span, _LOC_PATCH_SPAN_FIELDS, f"{label}.span")
    start = _non_negative_int(span.get("start"), f"{label}.span.start")
    end = _non_negative_int(span.get("end"), f"{label}.span.end")
    if end < start:
        raise ValueError(f"{label}.span.end must not be less than span.start.")
    expected = patch.get("expected")
    if not isinstance(expected, str):
        raise ValueError(f"{label}.expected must be a string.")
    if end - start != len(expected.encode("utf-16-le")) // 2:
        raise ValueError(f"{label}.span length must match expected in UTF-16 code units.")
    style = _required_string(patch.get("style"), f"{label}.style")
    if style not in _LOC_STYLES:
        supported = ", ".join(sorted(_LOC_STYLES))
        raise ValueError(f"{label}.style must be one of: {supported}.")
    newline = patch.get("newline")
    if newline not in {"\n", "\r\n"}:
        raise ValueError(f"{label}.newline must be LF or CRLF.")
    if style in {"inline", "yaml"} and any(character in expected for character in "\r\n"):
        raise ValueError(f"{label}.expected {style} text must stay on one line.")
    source_length = _non_negative_int(
        patch.get("source_length"),
        f"{label}.source_length",
    )
    if end > source_length:
        raise ValueError(f"{label}.span must stay inside source_length.")
    return {
        "op": "replace-loc-text",
        "path": path,
        "span": {"start": start, "end": end},
        "expected": expected,
        "style": style,
        "newline": newline,
        "source_length": source_length,
    }


def _normalize_pdx_patch(
    patch: Mapping[object, object],
    label: str,
) -> dict[str, object]:
    path = _normalize_pdx_patch_path(patch.get("path"), f"{label}.path")

    span = _required_mapping(patch.get("span"), f"{label}.span")
    _validate_fields(span, _PDX_PATCH_SPAN_FIELDS, f"{label}.span")
    start = _non_negative_int(span.get("start"), f"{label}.span.start")
    end = _non_negative_int(span.get("end"), f"{label}.span.end")
    if end <= start:
        raise ValueError(f"{label}.span.end must be greater than span.start.")
    expected = patch.get("expected")
    if not isinstance(expected, str) or not expected:
        raise ValueError(f"{label}.expected must be a non-empty string.")
    if end - start != len(expected.encode("utf-16-le")) // 2:
        raise ValueError(f"{label}.span length must match expected in UTF-16 code units.")
    scalar_kind = _required_string(
        patch.get("scalar_kind"),
        f"{label}.scalar_kind",
    )
    if scalar_kind not in _PDX_SCALAR_KINDS:
        supported = ", ".join(sorted(_PDX_SCALAR_KINDS))
        raise ValueError(f"{label}.scalar_kind must be one of: {supported}.")
    source_length = _non_negative_int(
        patch.get("source_length"),
        f"{label}.source_length",
    )
    if end > source_length:
        raise ValueError(f"{label}.span must stay inside source_length.")
    return {
        "op": "replace-pdx-scalar",
        "path": path,
        "span": {"start": start, "end": end},
        "expected": expected,
        "scalar_kind": scalar_kind,
        "source_length": source_length,
    }


def _normalize_pdx_integer_list_patch(
    patch: Mapping[object, object],
    label: str,
) -> dict[str, object]:
    path = _normalize_pdx_patch_path(patch.get("path"), f"{label}.path")
    span = _required_mapping(patch.get("span"), f"{label}.span")
    _validate_fields(span, _PDX_PATCH_SPAN_FIELDS, f"{label}.span")
    start = _non_negative_int(span.get("start"), f"{label}.span.start")
    end = _non_negative_int(span.get("end"), f"{label}.span.end")
    if end <= start:
        raise ValueError(f"{label}.span.end must be greater than span.start.")
    expected = patch.get("expected")
    if not isinstance(expected, str) or not expected.strip():
        raise ValueError(f"{label}.expected must contain at least one integer.")
    if end - start != len(expected.encode("utf-16-le")) // 2:
        raise ValueError(f"{label}.span length must match expected in UTF-16 code units.")
    if patch.get("item_kind") != "integer":
        raise ValueError(f"{label}.item_kind must be 'integer'.")
    columns = patch.get("columns")
    if type(columns) is not int or columns < 1 or columns > 16:
        raise ValueError(f"{label}.columns must be an integer from 1 to 16.")
    minimum = patch.get("minimum")
    if type(minimum) is not int or minimum < -_MAX_SAFE_JAVASCRIPT_INTEGER or minimum > _MAX_SAFE_JAVASCRIPT_INTEGER:
        raise ValueError(f"{label}.minimum must be a JavaScript-safe integer.")
    layout = _normalize_pdx_integer_list_layout(patch.get("layout"), f"{label}.layout")
    _normalized_pdx_integer_list(
        expected,
        columns=columns,
        minimum=minimum,
        label=f"{label}.expected",
    )
    source_length = _non_negative_int(
        patch.get("source_length"),
        f"{label}.source_length",
    )
    if end > source_length:
        raise ValueError(f"{label}.span must stay inside source_length.")
    return {
        "op": "replace-pdx-integer-list",
        "path": path,
        "span": {"start": start, "end": end},
        "expected": expected,
        "item_kind": "integer",
        "columns": columns,
        "minimum": minimum,
        "layout": layout,
        "source_length": source_length,
    }


def _normalize_pdx_block_body_patch(
    patch: Mapping[object, object],
    label: str,
) -> dict[str, object]:
    path = _normalize_pdx_patch_path(patch.get("path"), f"{label}.path")
    span = _required_mapping(patch.get("span"), f"{label}.span")
    _validate_fields(span, _PDX_PATCH_SPAN_FIELDS, f"{label}.span")
    start = _non_negative_int(span.get("start"), f"{label}.span.start")
    end = _non_negative_int(span.get("end"), f"{label}.span.end")
    if end < start:
        raise ValueError(f"{label}.span.end must not be less than span.start.")
    expected = patch.get("expected")
    if not isinstance(expected, str):
        raise ValueError(f"{label}.expected must be text.")
    if end - start != len(expected.encode("utf-16-le")) // 2:
        raise ValueError(f"{label}.span length must match expected in UTF-16 code units.")
    _normalized_pdx_block_body(expected, label=f"{label}.expected")
    layout = _normalize_pdx_block_body_layout(patch.get("layout"), f"{label}.layout")
    source_length = _non_negative_int(
        patch.get("source_length"),
        f"{label}.source_length",
    )
    if end > source_length:
        raise ValueError(f"{label}.span must stay inside source_length.")
    return {
        "op": "replace-pdx-block-body",
        "path": path,
        "span": {"start": start, "end": end},
        "expected": expected,
        "layout": layout,
        "source_length": source_length,
    }


def _normalize_pdx_patch_path(value: object, label: str) -> list[dict[str, object]]:
    raw_path = _required_sequence(value, label)
    if not raw_path:
        raise ValueError(f"{label} must be a non-empty list.")
    path: list[dict[str, object]] = []
    for index, raw_segment in enumerate(raw_path):
        segment_label = f"{label}[{index}]"
        segment = _required_mapping(raw_segment, segment_label)
        _validate_fields(segment, _PDX_PATCH_PATH_FIELDS, segment_label)
        key = _required_string(segment.get("key"), f"{segment_label}.key")
        occurrence = _non_negative_int(
            segment.get("occurrence"),
            f"{segment_label}.occurrence",
        )
        path.append({"key": key, "occurrence": occurrence})
    return path


def _normalize_pdx_integer_list_layout(value: object, label: str) -> dict[str, str]:
    layout = _required_mapping(value, label)
    _validate_fields(layout, _PDX_LIST_LAYOUT_FIELDS, label)
    normalized: dict[str, str] = {}
    for field in sorted(_PDX_LIST_LAYOUT_FIELDS):
        raw = layout.get(field)
        if not isinstance(raw, str):
            raise ValueError(f"{label}.{field} must be a string.")
        if len(raw) > 256 or any(character not in " \t\r\n" for character in raw):
            raise ValueError(f"{label}.{field} must contain at most 256 whitespace characters.")
        if field in {"column_separator", "row_separator"} and not raw:
            raise ValueError(f"{label}.{field} must not be empty.")
        normalized[field] = raw
    return normalized


def _normalize_pdx_block_body_layout(value: object, label: str) -> dict[str, str]:
    layout = _required_mapping(value, label)
    _validate_fields(layout, _PDX_BLOCK_LAYOUT_FIELDS, label)
    normalized: dict[str, str] = {}
    for field in sorted(_PDX_BLOCK_LAYOUT_FIELDS):
        raw = layout.get(field)
        if not isinstance(raw, str):
            raise ValueError(f"{label}.{field} must be a string.")
        if len(raw) > 256 or any(character not in " \t\r\n" for character in raw):
            raise ValueError(f"{label}.{field} must contain at most 256 whitespace characters.")
        if field == "line_prefix" and not raw:
            raise ValueError(f"{label}.{field} must not be empty.")
        normalized[field] = raw
    return normalized


def _json_patch_path(value: object, label: str) -> list[str | int]:
    raw_path = _required_sequence(value, label)
    if not raw_path:
        raise ValueError(f"{label} must be a non-empty list.")
    path: list[str | int] = []
    for index, segment in enumerate(raw_path):
        if isinstance(segment, str) and segment.strip():
            path.append(segment)
            continue
        if type(segment) is int and segment >= 0:
            path.append(segment)
            continue
        raise ValueError(f"{label}[{index}] must be a non-empty string or " "non-negative integer.")
    return path


def _required_mapping(value: object, label: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object.")
    return value


def _required_sequence(value: object, label: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{label} must be a list.")
    return value


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value


def _non_negative_int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _validate_fields(
    value: Mapping[object, object],
    allowed: frozenset[str],
    label: str,
) -> None:
    unknown = sorted(repr(key) for key in value if not isinstance(key, str) or key not in allowed)
    if unknown:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(unknown)}.")
