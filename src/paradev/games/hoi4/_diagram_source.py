"""Exact PDX source helpers shared by source-backed HoI4 diagrams.

The helpers in this internal module operate only on caller-provided text.
They do not discover projects, read files, or write drafts.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal

from heavenbase.utils import dumps_json, sha256hash

from paradev.pdx import (
    PDXBlock,
    PDXEntry,
    PDXParseError,
    PDXScalar,
    PDXTokenizer,
    TokenType,
    parse_pdx,
)


@dataclass(frozen=True, slots=True)
class DiagramLexToken:
    """One PDX token with exact source offsets."""

    kind: TokenType
    value: object
    start: int
    end: int
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class DiagramSourceDocument:
    """One parsed source snapshot used by an exact diagram planner."""

    path: str
    text: str
    sha256: str
    revision: str
    block: PDXBlock
    tokens: tuple[DiagramLexToken, ...]

    @property
    def significant_tokens(self) -> tuple[DiagramLexToken, ...]:
        """Return source tokens excluding comments and the EOF sentinel."""

        return tuple(token for token in self.tokens if token.kind not in {TokenType.COMMENT, TokenType.EOF})


@dataclass(frozen=True, slots=True)
class DiagramSourceReplacement:
    """One exact, guarded source replacement."""

    path: str
    start: int
    end: int
    expected: str
    replacement: str
    operations: tuple[str, ...]
    order_key: str


class UnsafeSourcePatch(ValueError):
    """Raised when an edit has no unambiguous local source patch."""


def whole_entry_line_replacement(
    document: DiagramSourceDocument,
    entry: PDXEntry,
    *,
    operation: str,
) -> DiagramSourceReplacement:
    """Return an exact replacement that removes one standalone PDX entry."""

    if entry_owns_comments(entry):
        raise UnsafeSourcePatch(f"Source entry for {operation} owns comments and cannot be removed " "without review.")
    key_token = scalar_token(document, entry.key)
    if isinstance(entry.val, PDXBlock):
        _, close_token = entry_block_tokens(document, entry)
        entry_end = close_token.end
    elif isinstance(entry.val, PDXScalar):
        entry_end = scalar_token(document, entry.val).end
    else:
        raise UnsafeSourcePatch(f"Source entry for {operation} has no safely bounded value.")
    line_start = document.text.rfind("\n", 0, key_token.start) + 1
    if document.text[line_start : key_token.start].strip():
        raise UnsafeSourcePatch(f"Source entry for {operation} is not on its own indented line.")
    newline_index = document.text.find("\n", entry_end)
    line_end = len(document.text) if newline_index < 0 else newline_index + 1
    suffix_end = len(document.text) if newline_index < 0 else newline_index
    if document.text[entry_end:suffix_end].strip():
        raise UnsafeSourcePatch(f"Source entry for {operation} has trailing source on its closing line.")
    return DiagramSourceReplacement(
        path=document.path,
        start=line_start,
        end=line_end,
        expected=document.text[line_start:line_end],
        replacement="",
        operations=(operation,),
        order_key=operation,
    )


def block_child_insertion(
    document: DiagramSourceDocument,
    entry: PDXEntry,
    block: PDXBlock,
) -> tuple[str, int]:
    """Return the indentation and exact offset for a block child insertion."""

    if block.trailing_comments:
        raise UnsafeSourcePatch("Target block owns trailing comments and cannot accept an insertion " "without review.")
    _, close_token = entry_block_tokens(document, entry)
    line_start = document.text.rfind("\n", 0, close_token.start) + 1
    close_indent = document.text[line_start : close_token.start]
    if close_indent.strip():
        raise UnsafeSourcePatch("Target block closing brace is not on its own indented line.")
    child_indents: list[str] = []
    for child in block.entries:
        if child.key is None:
            continue
        token = scalar_token(document, child.key)
        child_line_start = document.text.rfind("\n", 0, token.start) + 1
        prefix = document.text[child_line_start : token.start]
        if not prefix.strip() and prefix.startswith(close_indent) and len(prefix) > len(close_indent):
            child_indents.append(prefix)
    if child_indents:
        child_indent = min(child_indents, key=lambda value: (len(value), value))
    else:
        child_indent = close_indent + ("\t" if "\t" in close_indent else "    ")
    return child_indent, line_start


def indent_unit(
    document: DiagramSourceDocument,
    block: PDXBlock,
    child_indent: str,
) -> str:
    """Infer one nested indentation unit from a parsed block."""

    nested_indents: list[str] = []
    for child in block.entries:
        if not isinstance(child.val, PDXBlock):
            continue
        for nested in child.val.entries:
            if nested.key is None:
                continue
            token = scalar_token(document, nested.key)
            line_start = document.text.rfind("\n", 0, token.start) + 1
            prefix = document.text[line_start : token.start]
            if not prefix.strip() and prefix.startswith(child_indent) and len(prefix) > len(child_indent):
                nested_indents.append(prefix[len(child_indent) :])
    if nested_indents:
        return min(nested_indents, key=lambda value: (len(value), value))
    return "\t" if "\t" in child_indent else "    "


def merge_source_replacements(
    replacements: Sequence[DiagramSourceReplacement],
) -> list[DiagramSourceReplacement]:
    """Merge same-offset insertions and reject conflicting or overlapping edits."""

    by_path_and_range: dict[tuple[str, int, int], list[DiagramSourceReplacement]] = defaultdict(list)
    for replacement in replacements:
        by_path_and_range[(replacement.path, replacement.start, replacement.end)].append(replacement)
    merged: list[DiagramSourceReplacement] = []
    for (path, start, end), rows in sorted(by_path_and_range.items()):
        if len(rows) == 1:
            merged.append(rows[0])
            continue
        if start != end:
            first = rows[0]
            if any(row.expected != first.expected or row.replacement != first.replacement or row.operations != first.operations for row in rows[1:]):
                raise UnsafeSourcePatch(f"Source {path!r} has conflicting replacements for offsets " f"{start}:{end}.")
            merged.append(first)
            continue
        rows = sorted(rows, key=lambda row: row.order_key)
        merged.append(
            DiagramSourceReplacement(
                path=path,
                start=start,
                end=end,
                expected="",
                replacement="".join(row.replacement for row in rows),
                operations=tuple(operation for row in rows for operation in row.operations),
                order_key="|".join(row.order_key for row in rows),
            )
        )

    previous_by_path: dict[str, DiagramSourceReplacement] = {}
    for replacement in sorted(merged, key=lambda row: (row.path, row.start, row.end)):
        previous = previous_by_path.get(replacement.path)
        if previous is not None and replacement.start < previous.end:
            raise UnsafeSourcePatch(
                f"Source {replacement.path!r} has overlapping replacements at "
                f"{previous.start}:{previous.end} and "
                f"{replacement.start}:{replacement.end}."
            )
        previous_by_path[replacement.path] = replacement
    return sorted(merged, key=lambda row: (row.path, row.start, row.end, row.order_key))


def render_source_drafts(
    documents: Sequence[DiagramSourceDocument],
    replacements: Sequence[DiagramSourceReplacement],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Render guarded complete source drafts from exact replacements."""

    documents_by_path = {document.path: document for document in documents}
    replacements_by_path: dict[str, list[DiagramSourceReplacement]] = defaultdict(list)
    for replacement in replacements:
        replacements_by_path[replacement.path].append(replacement)
    drafts: list[dict[str, object]] = []
    replacement_rows: list[dict[str, object]] = []
    for path in sorted(replacements_by_path):
        document = documents_by_path[path]
        text = document.text
        rows = sorted(replacements_by_path[path], key=lambda row: (row.start, row.end))
        for replacement in rows:
            if document.text[replacement.start : replacement.end] != replacement.expected:
                raise UnsafeSourcePatch(f"Source {path!r} no longer matches the exact expected text " f"at {replacement.start}:{replacement.end}.")
        for replacement in reversed(rows):
            text = text[: replacement.start] + replacement.replacement + text[replacement.end :]
        try:
            parse_pdx(text)
        except PDXParseError as error:
            detail = "; ".join(row.message for row in error.diagnostics) or "unknown parser failure"
            raise UnsafeSourcePatch(f"Generated source {path!r} is not valid PDX: {detail}.") from error
        digest = text_sha256(text)
        drafts.append(
            {
                "path": path,
                "expected_source_revision": document.revision,
                "expected_sha256": document.sha256,
                "text": text,
                "sha256": digest,
                "source_revision": f"sha256:{digest}",
            }
        )
        replacement_rows.extend(
            {
                "path": replacement.path,
                "start": replacement.start,
                "end": replacement.end,
                "expected": replacement.expected,
                "replacement": replacement.replacement,
                "operations": list(replacement.operations),
            }
            for replacement in rows
        )
    replacement_rows.sort(
        key=lambda row: (
            str(row["path"]),
            int(row["start"]),
            int(row["end"]),
        )
    )
    return drafts, replacement_rows


def entry_block_tokens(
    document: DiagramSourceDocument,
    entry: PDXEntry,
) -> tuple[DiagramLexToken, DiagramLexToken]:
    """Resolve the opening and closing brace tokens for a keyed block entry."""

    if entry.key is None or entry.op is None or not isinstance(entry.val, PDXBlock):
        raise UnsafeSourcePatch("PDX entry is not a keyed block assignment.")
    key = scalar_token(document, entry.key)
    tokens = document.significant_tokens
    positions = [index for index, token in enumerate(tokens) if token.start == key.start]
    if len(positions) != 1:
        raise UnsafeSourcePatch("PDX block key does not resolve to one lexical token.")
    index = positions[0]
    if index + 2 >= len(tokens) or str(tokens[index + 1].value) != entry.op or tokens[index + 2].kind is not TokenType.LBRACE:
        raise UnsafeSourcePatch("PDX block assignment cannot be bounded without reformatting.")
    open_token = tokens[index + 2]
    depth = 0
    for token in tokens[index + 2 :]:
        if token.kind is TokenType.LBRACE:
            depth += 1
        elif token.kind is TokenType.RBRACE:
            depth -= 1
            if depth == 0:
                return open_token, token
    raise UnsafeSourcePatch("PDX block has no matching closing brace.")


def scalar_token(
    document: DiagramSourceDocument,
    scalar: PDXScalar | None,
) -> DiagramLexToken:
    """Resolve one parsed scalar to its exact lexical source token."""

    if scalar is None:
        raise UnsafeSourcePatch("PDX scalar is missing.")
    span = scalar.anno.get("span")
    if not isinstance(span, Mapping):
        raise UnsafeSourcePatch("PDX scalar has no source span.")
    line = span.get("line")
    column = span.get("column")
    if not isinstance(line, int) or not isinstance(column, int):
        raise UnsafeSourcePatch("PDX scalar source span is invalid.")
    matches = [token for token in document.tokens if token.line == line and token.column == column and token.kind not in {TokenType.COMMENT, TokenType.EOF}]
    if len(matches) != 1:
        raise UnsafeSourcePatch(f"PDX scalar at line {line}, column {column} does not resolve to one " "token.")
    token = matches[0]
    expected = document.text[token.start : token.end]
    if scalar.raw and expected != scalar.raw:
        raise UnsafeSourcePatch(f"PDX scalar at line {line}, column {column} does not match its " "parsed source token.")
    return token


def lex_pdx_tokens(text: str) -> tuple[DiagramLexToken, ...]:
    """Tokenize PDX text while retaining exact BOM-aware source offsets."""

    bom_offset = 1 if text.startswith("\ufeff") else 0
    visible = text[bom_offset:]
    line_starts = [0]
    line_starts.extend(index + 1 for index, char in enumerate(visible) if char == "\n")
    rows: list[DiagramLexToken] = []
    for token in PDXTokenizer(text).tokenize():
        if token.line < 1 or token.line > len(line_starts):
            raise UnsafeSourcePatch(f"PDX token reports invalid source line {token.line}.")
        start = bom_offset + line_starts[token.line - 1] + token.column - 1
        end = token_end(text, start, token.type, token.value)
        rows.append(
            DiagramLexToken(
                kind=token.type,
                value=token.value,
                start=start,
                end=end,
                line=token.line,
                column=token.column,
            )
        )
    return tuple(rows)


def token_end(
    text: str,
    start: int,
    kind: TokenType,
    value: object,
) -> int:
    """Return the exclusive exact offset for one PDX token."""

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
        return len(text)
    raw = str(value)
    end = start + len(raw)
    if text[start:end] != raw:
        raise UnsafeSourcePatch(f"PDX token at offset {start} does not match its lexical value.")
    return end


def entry_scalar_text(entry: PDXEntry) -> str | None:
    """Return one scalar entry's stripped text, if unambiguous."""

    if entry.op is None or not isinstance(entry.val, PDXScalar):
        return None
    return scalar_text(entry.val)


def scalar_text(scalar: PDXScalar) -> str | None:
    """Return one scalar's stripped evaluated text."""

    if scalar.val is None:
        return None
    value = str(scalar.val).strip()
    return value or None


def entry_number(entry: PDXEntry) -> int | float | None:
    """Return one finite numeric scalar entry."""

    if entry.op is None or not isinstance(entry.val, PDXScalar):
        return None
    value = entry.val.eval()
    return value if is_finite_number(value) else None


def is_finite_number(value: object) -> bool:
    """Return whether a value is a finite non-boolean integer or float."""

    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_utf8_text(value: str) -> bool:
    """Return whether text can be represented as UTF-8."""

    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def is_source_revision(value: object) -> bool:
    """Return whether a value is a canonical SHA-256 source revision."""

    if not isinstance(value, str) or len(value) != 71 or not value.startswith("sha256:"):
        return False
    return all(char in "0123456789abcdef" for char in value[7:])


def format_number(value: int | float) -> str:
    """Render a finite number as plain decimal PDX text."""

    if isinstance(value, int):
        return str(value)
    rendered = format(Decimal(str(value)), "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return "0" if rendered in {"-0", ""} else rendered


def source_span(scalar: PDXScalar | None) -> dict[str, int] | None:
    """Return a scalar's one-based source line and column."""

    if scalar is None:
        return None
    span = scalar.anno.get("span")
    if not isinstance(span, Mapping):
        return None
    line = span.get("line")
    column = span.get("column")
    if not isinstance(line, int) or not isinstance(column, int):
        return None
    return {"line": line, "column": column}


def source_newline(text: str, offset: int | None = None) -> str:
    """Infer the source newline convention around an optional offset."""

    if offset is not None and offset > 0 and text[offset - 1] == "\n":
        return "\r\n" if offset > 1 and text[offset - 2] == "\r" else "\n"
    return "\r\n" if "\r\n" in text else "\n"


def entry_owns_comments(entry: PDXEntry) -> bool:
    """Return whether removing an entry could discard attached comments."""

    if entry.comments or entry.inline_comment is not None:
        return True
    if not isinstance(entry.val, PDXBlock):
        return False
    if entry.val.trailing_comments:
        return True
    return any(entry_owns_comments(child) for child in entry.val.entries)


def text_sha256(text: str) -> str:
    """Return the repository-standard SHA-256 digest for exact text."""

    return sha256hash(text)


def stable_payload_hash(payload: Mapping[str, object]) -> str:
    """Return a deterministic SHA-256 digest for a JSON-safe payload."""

    return sha256hash(
        dumps_json(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            compact=True,
        )
    )
