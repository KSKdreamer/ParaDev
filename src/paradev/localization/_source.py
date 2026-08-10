"""Internal lossless parser for ParaDev localization source files."""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import canonical_language

_INVALID_HEADER = object()
_YAML_LANGUAGE = re.compile(
    r"^(?P<indent>\s*)(?P<language>[A-Za-z][A-Za-z0-9_-]*)\s*:\s*(?:#.*)?$",
    re.IGNORECASE,
)
_YAML_ENTRY = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.@?'\-]+)(?P<before>\s*):" r"(?P<version>\d*)(?P<after>\s*)(?P<value>.*)$")


@dataclass(frozen=True, slots=True)
class SourceEntry:
    """One parsed localization value with its exact source spans."""

    key: str
    language: str
    text: str
    expected: str
    start: int
    end: int
    occurrence: int
    style: str
    key_start: int
    key_end: int
    entry_start: int
    entry_end: int


@dataclass(frozen=True, slots=True)
class SourceRegion:
    """One localization-language or bracket-entry source region."""

    language: str
    language_token: str
    style: str
    start: int
    header_end: int
    body_start: int
    end: int


@dataclass(frozen=True, slots=True)
class SourceIssue:
    """One source-shape issue reported by the localization loader."""

    code: str
    line: int


@dataclass(frozen=True, slots=True)
class SourceDocument:
    """Parsed localization source plus exact editing metadata."""

    entries: tuple[SourceEntry, ...]
    issues: tuple[SourceIssue, ...]
    newline: str
    source_format: str
    regions: tuple[SourceRegion, ...]


@dataclass(frozen=True, slots=True)
class _Header:
    language: str
    language_token: str
    key: str | None
    key_start: int | None
    key_end: int | None


def parse_source(text: str) -> SourceDocument:
    """Parse a custom ``.loc`` or HoI4 ``.yml`` source losslessly.

    Format selection is deterministic and based on the first substantive
    source line. Both parsers retain exact value, key, and full-entry spans for
    revision-guarded authoring operations.
    """

    if not isinstance(text, str):
        raise TypeError("Localization source text must be a string.")
    for index, line in enumerate(text.splitlines()):
        body = line.removeprefix("\ufeff") if index == 0 else line
        stripped = body.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if _YAML_LANGUAGE.fullmatch(body) or _YAML_ENTRY.fullmatch(body):
            return parse_hoi4_yaml(text)
        break
    return parse_ini(text)


def parse_ini(text: str) -> SourceDocument:
    """Parse INI and bracket-section localization losslessly."""

    entries: list[SourceEntry] = []
    issues: list[SourceIssue] = []
    regions: list[SourceRegion] = []
    occurrences: dict[tuple[str, str], int] = {}
    language: str | None = None
    active_region: tuple[str, str, str, int, int, int] | None = None
    active_section: tuple[str, str, str, int, int, int, int] | None = None
    discard_until_header = False
    offset = 0

    def finish_region(end: int) -> None:
        nonlocal active_region
        if active_region is None:
            return
        region_language, token, style, start, header_end, body_start = active_region
        regions.append(
            SourceRegion(
                language=region_language,
                language_token=token,
                style=style,
                start=start,
                header_end=header_end,
                body_start=body_start,
                end=end,
            )
        )
        active_region = None

    def finish_section(end: int) -> None:
        nonlocal active_section
        if active_section is None:
            return
        (
            section_language,
            token,
            key,
            header_start,
            header_end,
            key_start,
            key_end,
        ) = active_section
        value_start, value_end = _trimmed_span(text, header_end, end)
        if value_start == value_end:
            value_start = value_end = header_end
        expected = text[value_start:value_end]
        _add_entry(
            entries,
            occurrences,
            key=key,
            language=section_language,
            text=_normalized_text(expected),
            expected=expected,
            start=value_start,
            end=value_end,
            style="section",
            key_start=key_start,
            key_end=key_end,
            entry_start=header_start,
            entry_end=end,
        )
        regions.append(
            SourceRegion(
                language=section_language,
                language_token=token,
                style="section",
                start=header_start,
                header_end=header_end,
                body_start=header_end,
                end=end,
            )
        )
        active_section = None

    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        line_start = offset
        offset += len(line)
        body = _line_body(line)
        logical_body = body.removeprefix("\ufeff") if line_number == 1 else body
        logical_start = line_start + len(body) - len(logical_body)
        stripped = logical_body.strip()
        header = _header(logical_body, logical_start)
        if header is _INVALID_HEADER:
            finish_section(line_start)
            finish_region(line_start)
            issues.append(SourceIssue(code="invalid_line", line=line_number))
            language = None
            discard_until_header = True
            continue
        if isinstance(header, _Header):
            finish_section(line_start)
            finish_region(line_start)
            language = header.language
            discard_until_header = False
            if header.key is None:
                active_region = (
                    header.language,
                    header.language_token,
                    "inline",
                    line_start,
                    offset,
                    offset,
                )
            else:
                assert header.key_start is not None and header.key_end is not None
                active_section = (
                    header.language,
                    header.language_token,
                    header.key,
                    line_start,
                    offset,
                    header.key_start,
                    header.key_end,
                )
            continue
        if discard_until_header or active_section is not None:
            continue
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if language is None:
            issues.append(SourceIssue(code="missing_language", line=line_number))
            continue
        if "=" not in logical_body:
            issues.append(SourceIssue(code="invalid_line", line=line_number))
            continue
        equals = logical_body.index("=")
        key, key_start, key_end = _key_span(
            logical_body[:equals],
            logical_start,
        )
        if not key:
            issues.append(SourceIssue(code="invalid_line", line=line_number))
            continue
        raw_text_start = logical_start + equals + 1
        value_start, value_end = _trimmed_span(
            text,
            raw_text_start,
            line_start + len(body),
        )
        expected = text[value_start:value_end]
        _add_entry(
            entries,
            occurrences,
            key=key,
            language=language,
            text=expected,
            expected=expected,
            start=value_start,
            end=value_end,
            style="inline",
            key_start=key_start,
            key_end=key_end,
            entry_start=line_start,
            entry_end=offset,
        )

    finish_section(len(text))
    finish_region(len(text))
    return SourceDocument(
        entries=tuple(entries),
        issues=tuple(issues),
        newline=_newline(text),
        source_format="ini",
        regions=tuple(regions),
    )


def parse_hoi4_yaml(text: str) -> SourceDocument:
    """Parse HoI4 localization YAML-like syntax without normalizing text."""

    entries: list[SourceEntry] = []
    issues: list[SourceIssue] = []
    regions: list[SourceRegion] = []
    occurrences: dict[tuple[str, str], int] = {}
    language: str | None = None
    language_token: str | None = None
    active_region: tuple[str, str, int, int, int] | None = None
    offset = 0

    def finish_region(end: int) -> None:
        nonlocal active_region
        if active_region is None:
            return
        region_language, token, start, header_end, body_start = active_region
        regions.append(
            SourceRegion(
                language=region_language,
                language_token=token,
                style="yaml",
                start=start,
                header_end=header_end,
                body_start=body_start,
                end=end,
            )
        )
        active_region = None

    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        line_start = offset
        offset += len(line)
        body = _line_body(line)
        logical_body = body.removeprefix("\ufeff") if line_number == 1 else body
        logical_start = line_start + len(body) - len(logical_body)
        stripped = logical_body.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        language_match = _YAML_LANGUAGE.fullmatch(logical_body)
        if language_match is not None and canonical_language(language_match.group("language")).startswith("l_"):
            finish_region(line_start)
            token = language_match.group("language")
            language = canonical_language(token)
            language_token = token
            active_region = (language, token, line_start, offset, offset)
            continue
        entry_match = _YAML_ENTRY.fullmatch(logical_body)
        if entry_match is None:
            issues.append(SourceIssue(code="invalid_line", line=line_number))
            continue
        if language is None or language_token is None:
            issues.append(SourceIssue(code="missing_language", line=line_number))
            continue
        key = entry_match.group("key")
        key_start = logical_start + entry_match.start("key")
        key_end = logical_start + entry_match.end("key")
        raw_value_start = logical_start + entry_match.start("value")
        parsed_value = _yaml_value(text, raw_value_start, line_start + len(body))
        if parsed_value is None:
            issues.append(SourceIssue(code="invalid_line", line=line_number))
            continue
        value_start, value_end, semantic = parsed_value
        expected = text[value_start:value_end]
        _add_entry(
            entries,
            occurrences,
            key=key,
            language=language,
            text=semantic,
            expected=expected,
            start=value_start,
            end=value_end,
            style="yaml",
            key_start=key_start,
            key_end=key_end,
            entry_start=line_start,
            entry_end=offset,
        )

    finish_region(len(text))
    return SourceDocument(
        entries=tuple(entries),
        issues=tuple(issues),
        newline=_newline(text),
        source_format="yaml",
        regions=tuple(regions),
    )


def _add_entry(
    entries: list[SourceEntry],
    occurrences: dict[tuple[str, str], int],
    *,
    key: str,
    language: str,
    text: str,
    expected: str,
    start: int,
    end: int,
    style: str,
    key_start: int,
    key_end: int,
    entry_start: int,
    entry_end: int,
) -> None:
    identity = (language, key)
    occurrence = occurrences.get(identity, 0)
    occurrences[identity] = occurrence + 1
    entries.append(
        SourceEntry(
            key=key,
            language=language,
            text=text,
            expected=expected,
            start=start,
            end=end,
            occurrence=occurrence,
            style=style,
            key_start=key_start,
            key_end=key_end,
            entry_start=entry_start,
            entry_end=entry_end,
        )
    )


def _header(body: str, body_start: int) -> _Header | object | None:
    stripped = body.strip()
    if not stripped.startswith("["):
        return None
    if not stripped.endswith("]") or len(stripped) < 3:
        return _INVALID_HEADER
    left = len(body) - len(body.lstrip())
    right = len(body.rstrip())
    inner_start = left + 1
    inner_end = right - 1
    raw_inner = body[inner_start:inner_end]
    leading = len(raw_inner) - len(raw_inner.lstrip())
    trailing = len(raw_inner.rstrip())
    header = raw_inner[leading:trailing]
    header_start = body_start + inner_start + leading
    if not header:
        return _INVALID_HEADER
    if "." in header:
        raw_language, raw_key = header.split(".", 1)
        language_token = raw_language.strip()
        key = raw_key.strip()
        if not key:
            return _INVALID_HEADER
        language = canonical_language(language_token)
        if not language.startswith("l_"):
            return None
        key_offset = header.index(".") + 1
        key_leading = len(raw_key) - len(raw_key.lstrip())
        key_start = header_start + key_offset + key_leading
        return _Header(
            language=language,
            language_token=language_token,
            key=key,
            key_start=key_start,
            key_end=key_start + len(key),
        )
    language_token = header.strip()
    language = canonical_language(language_token)
    if not language.startswith("l_"):
        return None
    return _Header(
        language=language,
        language_token=language_token,
        key=None,
        key_start=None,
        key_end=None,
    )


def _key_span(value: str, offset: int) -> tuple[str, int, int]:
    leading = len(value) - len(value.lstrip())
    stripped = value.strip()
    if ":" in stripped:
        name, version = stripped.rsplit(":", 1)
        if version.isdigit():
            stripped = name.rstrip()
    return stripped, offset + leading, offset + leading + len(stripped)


def _yaml_value(text: str, start: int, end: int) -> tuple[int, int, str] | None:
    start, end = _trimmed_span(text, start, end)
    if start == end:
        return None
    quote = text[start]
    if quote == '"':
        index = start + 1
        escaped = False
        while index < end:
            character = text[index]
            if character == '"' and not escaped:
                trailing = text[index + 1 : end].strip()
                if trailing and not trailing.startswith("#"):
                    return None
                token_end = index + 1
                return start, token_end, _unescape_double_quoted(text[start + 1 : index])
            if character == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
            index += 1
        return None
    if quote == "'":
        index = start + 1
        while index < end:
            if text[index] != "'":
                index += 1
                continue
            if index + 1 < end and text[index + 1] == "'":
                index += 2
                continue
            trailing = text[index + 1 : end].strip()
            if trailing and not trailing.startswith("#"):
                return None
            token_end = index + 1
            return start, token_end, text[start + 1 : index].replace("''", "'")
        return None
    raw = text[start:end]
    comment = re.search(r"\s+#", raw)
    if comment is not None:
        end = start + comment.start()
        start, end = _trimmed_span(text, start, end)
    return (start, end, text[start:end]) if start < end else None


def _unescape_double_quoted(value: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        if value[index] == "\\" and index + 1 < len(value) and value[index + 1] in {'"', "\\"}:
            output.append(value[index + 1])
            index += 2
            continue
        output.append(value[index])
        index += 1
    return "".join(output)


def _line_body(line: str) -> str:
    if line.endswith("\r\n"):
        return line[:-2]
    if line.endswith(("\n", "\r")):
        return line[:-1]
    return line


def _trimmed_span(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _normalized_text(value: str) -> str:
    return "\n".join(value.splitlines())


def _newline(text: str) -> str:
    without_crlf = text.replace("\r\n", "")
    if "\r" in without_crlf:
        raise ValueError("Localization source contains unsupported bare carriage returns.")
    if "\r\n" in text and "\n" in without_crlf:
        raise ValueError("Localization source mixes LF and CRLF line endings.")
    return "\r\n" if "\r\n" in text else "\n"
