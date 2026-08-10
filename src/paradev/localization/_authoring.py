"""Registry-facing localization workspace and lossless edit planners."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath

from . import canonical_language
from ._source import SourceDocument, SourceEntry, parse_source

MAX_LOCALIZATION_WORKSPACE_ROWS = 512
MAX_LOCALIZATION_WORKSPACE_LIMIT = 2048
_KEY = re.compile(r"^[A-Za-z0-9_.@?'\-]+$")
_OPERATION_FIELDS = {
    "set": frozenset({"op", "language", "key", "value", "source_path"}),
    "add": frozenset({"op", "key", "languages", "source_path"}),
    "rename": frozenset({"op", "key", "new_key"}),
    "remove": frozenset({"op", "key"}),
}


@dataclass(frozen=True, slots=True)
class LocalizationSource:
    """One revision-paired Registry-owned localization source draft."""

    path: str
    relative_path: str
    unit_relative_path: str
    slot: str
    text: str
    size: int
    mtime_ns: str


def localization_workspace(
    sources: Sequence[LocalizationSource],
    *,
    project_id: str,
    target_kind: str,
    target_id: str,
    family: str,
    object_id: str,
    source_root: str,
    limit: int = MAX_LOCALIZATION_WORKSPACE_ROWS,
) -> dict[str, object]:
    """Project one Registry-owned source unit into a localization table."""

    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LOCALIZATION_WORKSPACE_LIMIT:
        raise ValueError("Localization workspace limit must be an integer from 1 to " f"{MAX_LOCALIZATION_WORKSPACE_LIMIT}.")
    parsed = _parsed_sources(sources)
    languages: list[str] = []
    rows: dict[str, dict[str, dict[str, object]]] = {}
    seen: dict[tuple[str, str], str] = {}
    source_views: list[dict[str, object]] = []
    for source, document in parsed:
        source_languages: list[str] = []
        for region in document.regions:
            if region.language not in source_languages:
                source_languages.append(region.language)
        source_views.append(
            {
                "path": source.path,
                "relative_path": source.relative_path,
                "unit_relative_path": source.unit_relative_path,
                "slot": source.slot,
                "source_format": document.source_format,
                "languages": source_languages,
                "size": source.size,
                "mtime_ns": source.mtime_ns,
            }
        )
        for entry in document.entries:
            identity = (entry.language, entry.key)
            previous = seen.get(identity)
            if previous is not None:
                raise ValueError(f"Localization {entry.language}/{entry.key} is ambiguous: " f"{previous!r} and {source.relative_path!r}.")
            seen[identity] = source.relative_path
            if entry.language not in languages:
                languages.append(entry.language)
            rows.setdefault(entry.key, {})[entry.language] = {
                "text": entry.text,
                "source_path": source.path,
                "relative_path": source.relative_path,
                "slot": source.slot,
                "occurrence": entry.occurrence,
            }
    ordered_keys = sorted(rows, key=lambda value: (value.casefold(), value))
    shown_keys = ordered_keys[:limit]
    return {
        "schema": "paradev.localization-workspace.v2",
        "project_id": project_id,
        "target": {
            "kind": target_kind,
            "id": target_id,
            "family": family,
            "object_id": object_id,
        },
        "source_root": source_root,
        "languages": languages,
        "rows": [{"key": key, "values": rows[key]} for key in shown_keys],
        "sources": source_views,
        "coverage": {
            "truncated": len(shown_keys) < len(ordered_keys),
            "shown_rows": len(shown_keys),
            "total_rows": len(ordered_keys),
        },
    }


def plan_localization_operation(
    sources: Sequence[LocalizationSource],
    operation: Mapping[str, object],
    *,
    project_id: str,
    target_kind: str,
    target_id: str,
    family: str,
    object_id: str,
    source_root: str,
    limit: int = MAX_LOCALIZATION_WORKSPACE_ROWS,
) -> dict[str, object]:
    """Plan one closed localization operation without writing source files."""

    normalized = _operation(operation, object_id=object_id, sources=sources)
    current = {source.path: source.text for source in sources}
    changes: list[dict[str, object]] = []
    op = str(normalized["op"])
    if op == "set":
        _plan_set(sources, current, normalized, changes)
    elif op == "add":
        _plan_add(sources, current, normalized, changes)
    elif op == "rename":
        _plan_rename(sources, current, normalized, changes)
    else:
        _plan_remove(sources, current, normalized, changes)

    updated_sources = tuple(
        LocalizationSource(
            path=source.path,
            relative_path=source.relative_path,
            unit_relative_path=source.unit_relative_path,
            slot=source.slot,
            text=current[source.path],
            size=source.size,
            mtime_ns=source.mtime_ns,
        )
        for source in sources
    )
    source_edits = [
        {
            "path": source.path,
            "text": current[source.path],
            "expected_size": source.size,
            "expected_mtime_ns": source.mtime_ns,
        }
        for source in sources
        if current[source.path] != source.text
    ]
    return {
        "schema": "paradev.localization-update-plan.v2",
        "project_id": project_id,
        "target": {
            "kind": target_kind,
            "id": target_id,
            "family": family,
            "object_id": object_id,
        },
        "source_root": source_root,
        "operation": normalized,
        "changed": bool(source_edits),
        "changes": changes,
        "source_edits": source_edits,
        "workspace": localization_workspace(
            updated_sources,
            project_id=project_id,
            target_kind=target_kind,
            target_id=target_id,
            family=family,
            object_id=object_id,
            source_root=source_root,
            limit=limit,
        ),
    }


def _parsed_sources(
    sources: Sequence[LocalizationSource],
) -> tuple[tuple[LocalizationSource, SourceDocument], ...]:
    parsed: list[tuple[LocalizationSource, SourceDocument]] = []
    seen_paths: set[str] = set()
    for source in sources:
        if source.path in seen_paths:
            raise ValueError(f"Localization source path is repeated: {source.path!r}.")
        seen_paths.add(source.path)
        document = parse_source(source.text)
        if document.issues:
            issue = document.issues[0]
            raise ValueError(f"Localization source {source.relative_path!r} line {issue.line} " f"is invalid: {issue.code.replace('_', ' ')}.")
        parsed.append((source, document))
    return tuple(parsed)


def _operation(
    operation: Mapping[str, object],
    *,
    object_id: str,
    sources: Sequence[LocalizationSource],
) -> dict[str, object]:
    if not isinstance(operation, Mapping):
        raise ValueError("Localization operation must be an object.")
    op = operation.get("op")
    if not isinstance(op, str) or op not in _OPERATION_FIELDS:
        raise ValueError("Localization operation op must be 'set', 'add', 'rename', or 'remove'.")
    unknown = sorted(str(key) for key in set(operation) - _OPERATION_FIELDS[op])
    if unknown:
        raise ValueError(f"Localization {op} operation contains unsupported fields: {', '.join(unknown)}.")
    normalized: dict[str, object] = {"op": op}
    if op == "set":
        normalized.update(
            language=_language(operation.get("language"), "language"),
            key=_key(operation.get("key"), "key"),
            value=_text(operation.get("value"), "value"),
        )
    elif op == "add":
        existing = {entry.key for _source, document in _parsed_sources(sources) for entry in document.entries}
        raw_key = operation.get("key")
        normalized["key"] = _resolve_key(_key(raw_key, "key"), object_id) if raw_key is not None else _next_key(existing, object_id)
        raw_languages = operation.get("languages")
        if raw_languages is None:
            languages = [region.language for _source, document in _parsed_sources(sources) for region in document.regions]
            normalized["languages"] = list(dict.fromkeys(languages)) or ["l_english"]
        else:
            if isinstance(raw_languages, (str, bytes)) or not isinstance(raw_languages, Sequence) or not raw_languages:
                raise ValueError("Localization add languages must be a non-empty array.")
            languages = [_language(value, f"languages[{index}]") for index, value in enumerate(raw_languages)]
            if len(set(languages)) != len(languages):
                raise ValueError("Localization add languages must not repeat a language.")
            normalized["languages"] = languages
    elif op == "rename":
        normalized.update(
            key=_key(operation.get("key"), "key"),
            new_key=_resolve_key(_key(operation.get("new_key"), "new_key"), object_id),
        )
    else:
        normalized["key"] = _key(operation.get("key"), "key")
    if "source_path" in operation:
        source_path = _text(operation.get("source_path"), "source_path")
        if source_path not in {source.path for source in sources}:
            raise ValueError("Localization source_path is not owned by this target's Registry localization slots.")
        normalized["source_path"] = source_path
    return normalized


def _plan_set(
    sources: Sequence[LocalizationSource],
    current: dict[str, str],
    operation: Mapping[str, object],
    changes: list[dict[str, object]],
) -> None:
    language = str(operation["language"])
    key = str(operation["key"])
    value = str(operation["value"])
    matches = _entry_matches(sources, current, language=language, key=key)
    if len(matches) > 1:
        raise ValueError(f"Localization {language}/{key} is ambiguous and cannot be edited safely.")
    requested_path = operation.get("source_path")
    if matches:
        source, entry = matches[0]
        if requested_path is not None and requested_path != source.path:
            raise ValueError(f"Localization {language}/{key} belongs to a different source.")
        updated = _replace_value(current[source.path], entry, value)
        current[source.path] = updated
        if entry.text != value:
            changes.append(
                {
                    "op": "set",
                    "language": language,
                    "key": key,
                    "previous": entry.text,
                    "value": value,
                    "source_path": source.path,
                }
            )
        return
    source = _select_source(sources, current, language=language, requested_path=requested_path)
    current[source.path] = _insert_entry(
        current[source.path],
        language=language,
        key=key,
        value=value,
        suffix=PurePosixPath(source.unit_relative_path).suffix.casefold(),
    )
    changes.append(
        {
            "op": "add",
            "language": language,
            "key": key,
            "value": value,
            "source_path": source.path,
        }
    )


def _plan_add(
    sources: Sequence[LocalizationSource],
    current: dict[str, str],
    operation: Mapping[str, object],
    changes: list[dict[str, object]],
) -> None:
    key = str(operation["key"])
    if any(entry.key == key for _source, document in _parsed_current(sources, current) for entry in document.entries):
        raise ValueError(f"Localization key {key!r} already exists.")
    for language in operation["languages"]:
        source = _select_source(
            sources,
            current,
            language=str(language),
            requested_path=operation.get("source_path"),
        )
        current[source.path] = _insert_entry(
            current[source.path],
            language=str(language),
            key=key,
            value="",
            suffix=PurePosixPath(source.unit_relative_path).suffix.casefold(),
        )
        changes.append(
            {
                "op": "add",
                "language": language,
                "key": key,
                "value": "",
                "source_path": source.path,
            }
        )


def _plan_rename(
    sources: Sequence[LocalizationSource],
    current: dict[str, str],
    operation: Mapping[str, object],
    changes: list[dict[str, object]],
) -> None:
    key = str(operation["key"])
    new_key = str(operation["new_key"])
    if key == new_key:
        return
    parsed = _parsed_current(sources, current)
    matches = [(source, entry) for source, document in parsed for entry in document.entries if entry.key == key]
    if not matches:
        raise ValueError(f"Unknown localization key: {key!r}.")
    if any(entry.key == new_key for _source, document in parsed for entry in document.entries):
        raise ValueError(f"Localization key {new_key!r} already exists.")
    by_path: dict[str, list[SourceEntry]] = {}
    for source, entry in matches:
        by_path.setdefault(source.path, []).append(entry)
        changes.append(
            {
                "op": "rename",
                "language": entry.language,
                "key": key,
                "new_key": new_key,
                "source_path": source.path,
            }
        )
    for source in sources:
        entries = by_path.get(source.path)
        if entries:
            current[source.path] = _replace_spans(
                current[source.path],
                [(entry.key_start, entry.key_end, new_key) for entry in entries],
            )


def _plan_remove(
    sources: Sequence[LocalizationSource],
    current: dict[str, str],
    operation: Mapping[str, object],
    changes: list[dict[str, object]],
) -> None:
    key = str(operation["key"])
    parsed = _parsed_current(sources, current)
    matches = [(source, entry) for source, document in parsed for entry in document.entries if entry.key == key]
    if not matches:
        raise ValueError(f"Unknown localization key: {key!r}.")
    by_path: dict[str, list[SourceEntry]] = {}
    for source, entry in matches:
        by_path.setdefault(source.path, []).append(entry)
        changes.append(
            {
                "op": "remove",
                "language": entry.language,
                "key": key,
                "previous": entry.text,
                "source_path": source.path,
            }
        )
    for source in sources:
        entries = by_path.get(source.path)
        if entries:
            current[source.path] = _replace_spans(
                current[source.path],
                [(entry.entry_start, entry.entry_end, "") for entry in entries],
            )


def _entry_matches(
    sources: Sequence[LocalizationSource],
    current: Mapping[str, str],
    *,
    language: str,
    key: str,
) -> list[tuple[LocalizationSource, SourceEntry]]:
    return [
        (source, entry)
        for source, document in _parsed_current(sources, current)
        for entry in document.entries
        if entry.language == language and entry.key == key
    ]


def _parsed_current(
    sources: Sequence[LocalizationSource],
    current: Mapping[str, str],
) -> tuple[tuple[LocalizationSource, SourceDocument], ...]:
    return _parsed_sources(
        tuple(
            LocalizationSource(
                path=source.path,
                relative_path=source.relative_path,
                unit_relative_path=source.unit_relative_path,
                slot=source.slot,
                text=current[source.path],
                size=source.size,
                mtime_ns=source.mtime_ns,
            )
            for source in sources
        )
    )


def _select_source(
    sources: Sequence[LocalizationSource],
    current: Mapping[str, str],
    *,
    language: str,
    requested_path: object,
) -> LocalizationSource:
    if not sources:
        raise ValueError("This module has no Registry-owned localization source file.")
    if isinstance(requested_path, str):
        return next(source for source in sources if source.path == requested_path)
    parsed = _parsed_current(sources, current)
    for source, document in parsed:
        if any(region.language == language for region in document.regions):
            return source
    return sources[0]


def _replace_value(text: str, entry: SourceEntry, value: str) -> str:
    encoded = _encoded_value(value, entry.style, text=text, entry=entry)
    return text[: entry.start] + encoded + text[entry.end :]


def _encoded_value(value: str, style: str, *, text: str, entry: SourceEntry | None = None) -> str:
    if "\r" in value:
        raise ValueError("Localization text must use LF line endings.")
    if value != value.strip():
        raise ValueError("Localization text must not start or end with whitespace.")
    if style in {"inline", "yaml"} and "\n" in value:
        raise ValueError(f"{style.capitalize()} localization text must stay on one line.")
    if style == "yaml":
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if style == "inline":
        return value
    if style != "section":
        raise ValueError(f"Unsupported localization source style: {style!r}.")
    probe = f"[en.PARADEV_VALUE]\n{value}\n[en.PARADEV_SENTINEL]\nvalue\n"
    parsed = parse_source(probe)
    if parsed.issues or len(parsed.entries) != 2 or parsed.entries[0].text != value:
        raise ValueError("Localization text contains a source section header.")
    newline = parse_source(text).newline
    if entry is not None and entry.start == entry.end and value and entry.end < len(text) and text[entry.end] == "[":
        return value.replace("\n", newline) + newline
    return value.replace("\n", newline)


def _insert_entry(text: str, *, language: str, key: str, value: str, suffix: str) -> str:
    document = parse_source(text)
    if document.issues:
        issue = document.issues[0]
        raise ValueError(f"Localization source line {issue.line} is invalid: {issue.code.replace('_', ' ')}.")
    if any(entry.language == language and entry.key == key for entry in document.entries):
        raise ValueError(f"Localization {language}/{key} already exists.")
    same_language = [region for region in document.regions if region.language == language]
    if document.source_format == "yaml" or suffix in {".yml", ".yaml"}:
        style = "yaml"
    elif any(region.style == "section" for region in document.regions) or not document.regions:
        style = "section"
    else:
        style = "inline"
    position = same_language[-1].end if same_language else len(text)
    newline = document.newline
    prefix = "" if position == 0 or text[:position].endswith(("\n", "\r")) else newline
    if style == "yaml":
        header = "" if same_language else f"{language}:{newline}"
        addition = f"{header} {key}:0 {_encoded_value(value, 'yaml', text=text)}{newline}"
    elif style == "inline":
        token = same_language[-1].language_token if same_language else language
        header = "" if same_language else f"[{token}]{newline}"
        addition = f"{header}{key}={value}{newline}"
    else:
        token = same_language[-1].language_token if same_language else _short_language(language)
        body = value.replace("\n", newline)
        addition = f"[{token}.{key}]{newline}{body}{newline}"
    return text[:position] + prefix + addition + text[position:]


def _replace_spans(text: str, replacements: Sequence[tuple[int, int, str]]) -> str:
    ordered = sorted(replacements)
    for previous, current in zip(ordered, ordered[1:]):
        if current[0] < previous[1]:
            raise ValueError("Localization edit spans overlap.")
    updated = text
    for start, end, value in reversed(ordered):
        updated = updated[:start] + value + updated[end:]
    return updated


def _language(value: object, label: str) -> str:
    language = canonical_language(_text(value, label))
    if not language.startswith("l_"):
        raise ValueError(f"Localization {label} must resolve to an l_ language id.")
    return language


def _key(value: object, label: str) -> str:
    key = _text(value, label).strip()
    if not _KEY.fullmatch(key):
        raise ValueError(f"Localization {label} contains unsupported characters.")
    return key


def _text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Localization {label} must be a string.")
    return value


def _resolve_key(key: str, object_id: str) -> str:
    if not key.startswith("@"):
        return key
    suffix = key[1:]
    if not suffix:
        return object_id
    return f"{object_id}{suffix}" if suffix.startswith("_") else f"{object_id}_{suffix}"


def _next_key(existing: set[str], object_id: str) -> str:
    base = f"{object_id}_NEW"
    if base not in existing:
        return base
    index = 2
    while f"{base}_{index}" in existing:
        index += 1
    return f"{base}_{index}"


def _short_language(language: str) -> str:
    return {"l_english": "en", "l_simp_chinese": "zh"}.get(language, language.removeprefix("l_"))
