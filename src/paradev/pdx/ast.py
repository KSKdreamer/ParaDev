"""PDX AST records and formatting helpers."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, overload

SCALAR_ID = "id"
SCALAR_NUM = "num"
SCALAR_STR = "str"
SCALAR_BOOL = "bool"
SCALAR_VAR = "var"
SCALAR_COLOR = "color"


@dataclass(slots=True)
class PDXScalar:
    """A leaf scalar in a PDX document.

    Args:
        val: Parsed scalar value.
        raw: Original renderable source text.
        type: Scalar type tag.
        anno: Optional annotations for downstream tooling.
    """

    val: Any = None
    raw: str = ""
    type: str = SCALAR_ID
    anno: dict[str, Any] = field(default_factory=dict)

    @property
    def value(self) -> Any:
        """Return the scalar value."""

        return self.val

    def to_str(self) -> str:
        """Render the scalar as PDX source text."""

        if self.raw:
            return self.raw
        if self.type == SCALAR_STR:
            escaped = str(self.val).replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return "" if self.val is None else str(self.val)

    def eval(self) -> Any:
        """Return a JSON-safe best-effort Python value."""

        return _eval_scalar(self)

    def dump(self) -> dict[str, Any]:
        """Return a lossless JSON-safe scalar payload."""

        data: dict[str, Any] = {"val": self.val, "raw": self.raw, "type": self.type}
        if self.anno:
            data["anno"] = self.anno
        return data

    @classmethod
    def load(cls, data: dict[str, Any]) -> "PDXScalar":
        """Restore a scalar from :meth:`dump` output.

        Args:
            data: Serialized scalar payload.

        Returns:
            Restored scalar.
        """

        return cls(val=data.get("val"), raw=data.get("raw", ""), type=data.get("type", SCALAR_ID), anno=data.get("anno", {}))

    def clone(self) -> "PDXScalar":
        """Return an independent scalar copy."""

        return PDXScalar(
            val=copy.deepcopy(self.val),
            raw=self.raw,
            type=self.type,
            anno=copy.deepcopy(self.anno),
        )

    @staticmethod
    def id(value: str) -> "PDXScalar":
        """Create a bare identifier scalar."""

        return PDXScalar(val=value, raw=value, type=SCALAR_ID)

    @staticmethod
    def make(value: Any) -> "PDXScalar":
        """Create a scalar from a Python value."""

        if isinstance(value, bool):
            raw = "yes" if value else "no"
            return PDXScalar(val=raw, raw=raw, type=SCALAR_BOOL)
        if isinstance(value, int):
            raw = str(value)
            return PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)
        if isinstance(value, float):
            raw = f"{value:g}"
            return PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)
        if isinstance(value, str):
            if value.startswith("@"):
                return PDXScalar(val=value, raw=value, type=SCALAR_VAR)
            if re.match(r"^(rgb|hsv)\s*\{", value, re.IGNORECASE):
                return PDXScalar(val=value, raw=value, type=SCALAR_COLOR)
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return PDXScalar(val=value, raw=f'"{escaped}"', type=SCALAR_STR)
        return PDXScalar(val=str(value), raw=str(value), type=SCALAR_ID)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PDXScalar):
            return NotImplemented
        return self.val == other.val and self.type == other.type

    def __hash__(self) -> int:
        return hash((self.val, self.type))


@dataclass(slots=True)
class PDXEntry:
    """One PDX entry: keyed value, bare value, comparison, or anonymous block."""

    key: PDXScalar | None = None
    op: str | None = None
    val: PDXScalar | "PDXBlock" | None = None
    comments: list[str] = field(default_factory=list)
    inline_comment: str | None = None
    anno: dict[str, Any] = field(default_factory=dict)

    @property
    def key_str(self) -> str | None:
        """Return the key as text when present."""

        return str(self.key.val) if self.key else None

    @property
    def value(self) -> Any:
        """Return the evaluated scalar value or nested block."""

        if isinstance(self.val, PDXScalar):
            return self.val.eval()
        return self.val

    @property
    def is_kv(self) -> bool:
        """Return whether this entry is a keyed operator entry."""

        return self.key is not None and self.op is not None

    @property
    def is_bare(self) -> bool:
        """Return whether this entry is a bare value."""

        return self.key is not None and self.op is None and self.val is None

    @property
    def is_anonymous(self) -> bool:
        """Return whether this entry is an anonymous nested block."""

        return self.key is None and isinstance(self.val, PDXBlock)

    @classmethod
    def from_str(cls, text: str) -> "PDXEntry":
        """Parse a single entry from PDX text.

        Args:
            text: PDX source text.

        Returns:
            First parsed entry.

        Raises:
            ValueError: If no entry exists in the text.
        """

        block = PDXBlock.from_str(text)
        if not block.entries:
            raise ValueError("No entry found in text")
        return block.entries[0]

    @classmethod
    def from_tokens(cls, tokens: Iterable[Any]) -> "PDXEntry":
        """Parse a single entry from tokens."""

        block = PDXBlock.from_tokens(tokens)
        if not block.entries:
            raise ValueError("No entry found in tokens")
        return block.entries[0]

    def to_str(self, indent: str = "\t", level: int = 0, comments: bool = True) -> str:
        """Render the entry as PDX source text."""

        return _format_entry(self, indent=indent, level=level, comments=comments)

    def to_tokens(self, comments: bool = True) -> list[Any]:
        """Return tokens representing this entry."""

        tokens: list[Any] = []
        _emit_entry_tokens(self, tokens, comments=comments)
        return tokens

    def dump(self) -> dict[str, Any]:
        """Return a lossless JSON-safe entry payload."""

        data: dict[str, Any] = {}
        if self.key is not None:
            data["key"] = self.key.dump()
        if self.op is not None:
            data["op"] = self.op
        if isinstance(self.val, PDXScalar):
            data["val"] = self.val.dump()
        elif isinstance(self.val, PDXBlock):
            data["val"] = self.val.dump()
        if self.comments:
            data["comments"] = self.comments
        if self.inline_comment is not None:
            data["inline_comment"] = self.inline_comment
        if self.anno:
            data["anno"] = self.anno
        return data

    @classmethod
    def load(cls, data: dict[str, Any]) -> "PDXEntry":
        """Restore an entry from :meth:`dump` output."""

        val_data = data.get("val")
        val: PDXScalar | PDXBlock | None = None
        if isinstance(val_data, dict):
            val = PDXBlock.load(val_data) if "entries" in val_data else PDXScalar.load(val_data)
        return cls(
            key=PDXScalar.load(data["key"]) if "key" in data else None,
            op=data.get("op"),
            val=val,
            comments=list(data.get("comments", [])),
            inline_comment=data.get("inline_comment"),
            anno=dict(data.get("anno", {})),
        )

    def clone(self) -> "PDXEntry":
        """Return an independent entry copy."""

        value = self.val.clone() if self.val is not None else None
        return PDXEntry(
            key=self.key.clone() if self.key is not None else None,
            op=self.op,
            val=value,
            comments=list(self.comments),
            inline_comment=self.inline_comment,
            anno=copy.deepcopy(self.anno),
        )

    @staticmethod
    def kv(key: str, value: Any, op: str = "=") -> "PDXEntry":
        """Create a ``key op value`` entry."""

        scalar_key = PDXScalar.id(key)
        if isinstance(value, (PDXBlock, PDXScalar)):
            val = value
        elif isinstance(value, (dict, list, tuple)):
            val = PDXBlock.from_dict(value)
        else:
            val = PDXScalar.make(value)
        return PDXEntry(key=scalar_key, op=op, val=val)

    @staticmethod
    def kv_id(key: str, value: str, op: str = "=") -> "PDXEntry":
        """Create a keyed entry with an identifier value."""

        return PDXEntry(key=PDXScalar.id(key), op=op, val=PDXScalar.id(value))

    @staticmethod
    def bare(value: Any) -> "PDXEntry":
        """Create a bare value entry."""

        if isinstance(value, PDXScalar):
            return PDXEntry(key=value)
        if isinstance(value, PDXBlock):
            return PDXEntry(val=value)
        return PDXEntry(key=PDXScalar.id(str(value)))


@dataclass(slots=True)
class PDXBlock:
    """Container of :class:`PDXEntry` items and primary public PDX API."""

    entries: list[PDXEntry] = field(default_factory=list)
    trailing_comments: list[str] = field(default_factory=list)
    anno: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_str(cls, text: str) -> "PDXBlock":
        """Parse PDX source text into a block.

        Args:
            text: PDX source text.

        Returns:
            Parsed block.

        Raises:
            PDXParseError: If the token stream contains unbalanced blocks.
        """

        from .parser import parse_pdx

        return parse_pdx(text)

    @classmethod
    def from_entries(cls, entries: Iterable[PDXEntry]) -> "PDXBlock":
        """Build a block from entries."""

        return cls(entries=list(entries))

    @classmethod
    def from_tokens(cls, tokens: Iterable[Any]) -> "PDXBlock":
        """Parse tokens into a block."""

        from .parser import PDXParser

        return PDXParser(list(tokens)).run()

    @classmethod
    def from_dict(cls, data: Any) -> "PDXBlock":
        """Build a block from the lossy :meth:`to_dict` shape."""

        return _from_dict(data)

    @classmethod
    def from_file(cls, path: str | Path) -> "PDXBlock":
        """Read and parse a UTF-8 or UTF-8-BOM PDX file."""

        source = Path(path)
        block = cls.from_str(source.read_text(encoding="utf-8-sig", errors="replace"))
        block.file_ext = source.suffix or None
        return block

    @property
    def file_ext(self) -> str | None:
        """Return the source file extension when known."""

        return self.anno.get("file_ext")

    @file_ext.setter
    def file_ext(self, value: str | None) -> None:
        if value is None:
            self.anno.pop("file_ext", None)
        else:
            self.anno["file_ext"] = value

    def to_str(self, indent: str = "\t", comments: bool = True) -> str:
        """Render this block as formatted PDX text."""

        text = _format_block(self, indent=indent, level=0, comments=comments)
        return f"{text}\n" if text else ""

    def to_file(self, path: str | Path, indent: str = "\t", comments: bool = True) -> None:
        """Write formatted PDX text to a file."""

        target = Path(path)
        if not target.suffix and self.file_ext:
            target = target.with_suffix(self.file_ext)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.to_str(indent=indent, comments=comments), encoding="utf-8")

    def to_dict(self) -> Any:
        """Return a deterministic lossy JSON-safe projection."""

        return _block_to_dict(self)

    def to_tokens(self, comments: bool = True) -> list[Any]:
        """Return tokens representing this block."""

        from .token import Token, TokenType

        tokens: list[Any] = []
        _emit_tokens(self, tokens, comments=comments)
        tokens.append(Token(TokenType.EOF))
        return tokens

    def dump(self) -> dict[str, Any]:
        """Return a lossless JSON-safe block payload."""

        data: dict[str, Any] = {"entries": [entry.dump() for entry in self.entries]}
        if self.trailing_comments:
            data["trailing_comments"] = self.trailing_comments
        if self.anno:
            data["anno"] = self.anno
        return data

    @classmethod
    def load(cls, data: Any) -> "PDXBlock":
        """Restore a block from :meth:`dump` output or a JSON file."""

        if isinstance(data, (str, Path)):
            data = json.loads(Path(data).read_text(encoding="utf-8"))
        block = cls()
        block.entries = [PDXEntry.load(entry) for entry in data.get("entries", [])]
        block.trailing_comments = list(data.get("trailing_comments", []))
        block.anno = dict(data.get("anno", {}))
        return block

    def save(self, path: str | Path, indent: int = 2) -> None:
        """Write lossless JSON serialization to a file."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.dump(), ensure_ascii=False, indent=indent), encoding="utf-8")

    def clone(self) -> "PDXBlock":
        """Return an independent block copy."""

        return PDXBlock(
            entries=[entry.clone() for entry in self.entries],
            trailing_comments=list(self.trailing_comments),
            anno=copy.deepcopy(self.anno),
        )

    @overload
    def __getitem__(self, key: int) -> PDXEntry: ...

    @overload
    def __getitem__(self, key: str) -> Any: ...

    @overload
    def __getitem__(self, key: slice) -> list[PDXEntry]: ...

    def __getitem__(self, key: str | int | slice | tuple[str, int]) -> Any:
        if isinstance(key, tuple):
            name, index = key
            matches = [entry for entry in self.entries if entry.key and str(entry.key.val) == name]
            if not matches:
                raise KeyError(name)
            return matches[index].val
        if isinstance(key, (int, slice)):
            return self.entries[key]
        for entry in self.entries:
            if entry.key and str(entry.key.val) == key:
                return entry.val
        raise KeyError(key)

    @overload
    def __setitem__(self, key: int, value: PDXEntry) -> None: ...

    @overload
    def __setitem__(self, key: str, value: Any) -> None: ...

    @overload
    def __setitem__(self, key: slice, value: Sequence[PDXEntry]) -> None: ...

    def __setitem__(self, key: str | int | slice | tuple[str, int], value: Any) -> None:
        if isinstance(key, tuple):
            name, index = key
            matches = [entry for entry in self.entries if entry.key and str(entry.key.val) == name]
            if not matches:
                raise KeyError(name)
            _set_entry_value(matches[index], value)
            return
        if isinstance(key, int):
            if not isinstance(value, PDXEntry):
                raise TypeError("Integer index requires a PDXEntry value")
            self.entries[key] = value
            return
        if isinstance(key, slice):
            self.entries[key] = value
            return
        for entry in self.entries:
            if entry.key and str(entry.key.val) == key:
                _set_entry_value(entry, value)
                return
        self.add(key, value)

    def __delitem__(self, key: str | int | slice | tuple[str, int]) -> None:
        if isinstance(key, tuple):
            name, index = key
            matches = [(idx, entry) for idx, entry in enumerate(self.entries) if entry.key and str(entry.key.val) == name]
            if not matches:
                raise KeyError(name)
            del self.entries[matches[index][0]]
            return
        if isinstance(key, (int, slice)):
            del self.entries[key]
            return
        for index, entry in enumerate(self.entries):
            if entry.key and str(entry.key.val) == key:
                del self.entries[index]
                return
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return any(entry.key and str(entry.key.val) == key for entry in self.entries)

    def __iter__(self) -> Iterator[PDXEntry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __bool__(self) -> bool:
        return True

    def __reversed__(self) -> Iterator[PDXEntry]:
        return reversed(self.entries)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the first matching entry value or a default."""

        for entry in self.entries:
            if entry.key and str(entry.key.val) == key:
                return entry.val
        return default

    def keys(self) -> list[str]:
        """Return all keyed entry names, including duplicates."""

        return [str(entry.key.val) for entry in self.entries if entry.key]

    def values(self) -> list[Any]:
        """Return entry values or bare scalar keys."""

        result: list[Any] = []
        for entry in self.entries:
            if entry.op:
                result.append(entry.val)
            elif entry.key:
                result.append(entry.key)
        return result

    def items(self) -> list[tuple[str, Any]]:
        """Return keyed operator entries as ``(key, value)`` pairs."""

        return [(str(entry.key.val), entry.val) for entry in self.entries if entry.key and entry.op]

    def find(self, key: str, **kwargs: Any) -> PDXEntry | None:
        """Return the first matching entry."""

        for entry in self.entries:
            if entry.key and str(entry.key.val) == key and (not kwargs or _match_kwargs(entry, kwargs)):
                return entry
        return None

    def find_all(self, key: str, **kwargs: Any) -> list[PDXEntry]:
        """Return all matching entries."""

        return [entry for entry in self.entries if entry.key and str(entry.key.val) == key and (not kwargs or _match_kwargs(entry, kwargs))]

    def index(self, key: str) -> int:
        """Return the first matching entry index."""

        for index, entry in enumerate(self.entries):
            if entry.key and str(entry.key.val) == key:
                return index
        raise ValueError(f"{key!r} is not in PDXBlock")

    def count(self, key: str) -> int:
        """Return the number of entries with a given key."""

        return sum(1 for entry in self.entries if entry.key and str(entry.key.val) == key)

    def add(self, key: str, value: Any = None, op: str = "=") -> PDXEntry:
        """Append a keyed entry and return it."""

        entry = PDXEntry.kv(key, value, op=op)
        self.entries.append(entry)
        return entry

    def append(self, entry: PDXEntry) -> None:
        """Append an entry."""

        self.entries.append(entry)

    def extend(self, entries: Iterable[PDXEntry]) -> None:
        """Append several entries."""

        self.entries.extend(entries)

    def insert(self, index: int, entry: PDXEntry) -> None:
        """Insert an entry."""

        self.entries.insert(index, entry)

    def pop(self, index: int = -1) -> PDXEntry:
        """Remove and return an entry."""

        return self.entries.pop(index)

    def remove(self, key: str) -> int:
        """Remove all entries with a key and return the count removed."""

        before = len(self.entries)
        self.entries = [entry for entry in self.entries if not (entry.key and str(entry.key.val) == key)]
        return before - len(self.entries)

    def clear(self) -> None:
        """Remove all entries and trailing comments."""

        self.entries.clear()
        self.trailing_comments.clear()

    def walk(self) -> Iterator[tuple[list[str], PDXEntry]]:
        """Yield ``(path, entry)`` pairs depth-first."""

        yield from _walk(self, [])

    def __add__(self, other: "PDXBlock") -> "PDXBlock":
        if not isinstance(other, PDXBlock):
            return NotImplemented
        return PDXBlock(entries=self.entries + other.entries)

    def __iadd__(self, other: "PDXBlock") -> "PDXBlock":
        if not isinstance(other, PDXBlock):
            return NotImplemented
        self.entries.extend(other.entries)
        return self


def _set_entry_value(entry: PDXEntry, value: Any) -> None:
    if isinstance(value, (PDXBlock, PDXScalar)):
        entry.val = value
    elif isinstance(value, (dict, list, tuple)):
        entry.val = PDXBlock.from_dict(value)
    else:
        entry.val = PDXScalar.make(value)
    entry.op = entry.op or "="


def _walk(block: PDXBlock, path: list[str]) -> Iterator[tuple[list[str], PDXEntry]]:
    for entry in block.entries:
        key = str(entry.key.val) if entry.key else None
        current = path + [key] if key else path
        yield current, entry
        if isinstance(entry.val, PDXBlock):
            yield from _walk(entry.val, current)


def _match_kwargs(entry: PDXEntry, kwargs: dict[str, Any]) -> bool:
    if not isinstance(entry.val, PDXBlock):
        return False
    for key, value in kwargs.items():
        sub = entry.val.find(key)
        if sub is None:
            return False
        if isinstance(sub.val, PDXScalar) and (sub.val.eval() == value or sub.val.val == value):
            continue
        if isinstance(sub.val, PDXBlock) and sub.val == value:
            continue
        return False
    return True


def _format_entry(entry: PDXEntry, indent: str, level: int, comments: bool = True) -> str:
    lines: list[str] = []
    prefix = indent * level
    if comments:
        lines.extend(f"{prefix}{comment}" for comment in entry.comments)

    suffix = f"  {entry.inline_comment}" if comments and entry.inline_comment else ""
    if entry.key is None and isinstance(entry.val, PDXBlock):
        lines.append(f"{prefix}{{{suffix}")
        inner = _format_block(entry.val, indent=indent, level=level + 1, comments=comments)
        if inner:
            lines.append(inner)
        lines.append(f"{prefix}}}")
    elif entry.op and isinstance(entry.val, PDXBlock):
        lines.append(f"{prefix}{entry.key.to_str()} {entry.op} {{{suffix}")
        inner = _format_block(entry.val, indent=indent, level=level + 1, comments=comments)
        if inner:
            lines.append(inner)
        lines.append(f"{prefix}}}")
    elif entry.op and entry.val is not None:
        lines.append(f"{prefix}{entry.key.to_str()} {entry.op} {entry.val.to_str()}{suffix}")
    elif entry.op:
        lines.append(f"{prefix}{entry.key.to_str()} {entry.op}{suffix}")
    elif entry.key:
        lines.append(f"{prefix}{entry.key.to_str()}{suffix}")
    return "\n".join(lines)


def _format_block(block: PDXBlock, indent: str, level: int, comments: bool = True) -> str:
    lines = [text for entry in block.entries if (text := _format_entry(entry, indent=indent, level=level, comments=comments))]
    if comments:
        prefix = indent * level
        lines.extend(f"{prefix}{comment}" for comment in block.trailing_comments)
    return "\n".join(lines)


def _unescape(text: str) -> str:
    out: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "\\" and index + 1 < len(text):
            out.append(text[index + 1])
            index += 2
        else:
            out.append(text[index])
            index += 1
    return "".join(out)


def _eval_scalar(scalar: PDXScalar) -> Any:
    if scalar.type == SCALAR_BOOL:
        return scalar.val == "yes"
    if scalar.type == SCALAR_STR:
        return _unescape(str(scalar.val))
    if scalar.type == SCALAR_COLOR:
        return scalar.val
    if scalar.type == SCALAR_NUM:
        for caster in (int, float):
            try:
                return caster(scalar.val)
            except (TypeError, ValueError):
                pass
        return scalar.val
    if scalar.val == "yes":
        return True
    if scalar.val == "no":
        return False
    for caster in (int, float):
        try:
            return caster(scalar.val)
        except (TypeError, ValueError):
            pass
    return scalar.val


def _dedupe_key(key: str, data: dict[str, Any]) -> str:
    if key not in data:
        return key
    index = 1
    while f"{key}__D{index}" in data:
        index += 1
    return f"{key}__D{index}"


def _skip_entry(entry: PDXEntry) -> bool:
    return bool(entry.key and isinstance(entry.key.val, str) and entry.key.val.startswith("§"))


def _block_to_dict(block: PDXBlock) -> Any:
    entries = [entry for entry in block.entries if not _skip_entry(entry)]
    if not entries:
        return []
    if not any(entry.op for entry in entries):
        values: list[Any] = []
        for entry in entries:
            if entry.key is None and isinstance(entry.val, PDXBlock):
                values.append(_block_to_dict(entry.val))
            elif entry.key is not None:
                values.append(_eval_scalar(entry.key))
            else:
                values.append(None)
        return values

    data: dict[str, Any] = {}
    for entry in entries:
        if entry.key is None and isinstance(entry.val, PDXBlock):
            data[_dedupe_key("_anonymous_block", data)] = _block_to_dict(entry.val)
        elif entry.op and entry.op != "=":
            key = f"{entry.key.val} {entry.op} {entry.val.val}" if isinstance(entry.val, PDXScalar) else str(entry.key.val)
            data[_dedupe_key(key, data)] = None
        elif entry.op == "=":
            key = str(entry.key.val)
            if isinstance(entry.val, PDXBlock):
                value = _block_to_dict(entry.val)
            elif isinstance(entry.val, PDXScalar):
                value = _eval_scalar(entry.val)
            else:
                value = None
            data[_dedupe_key(key, data)] = value
        elif entry.key:
            data[_dedupe_key(str(entry.key.val), data)] = None
    return data


_DUP_RE = re.compile(r"__D\d+$")
_CMP_RE = re.compile(r"^(.+?)\s+(>=|<=|!=|>|<)\s+(.+)$")


def _make_dict_value(value: Any) -> PDXScalar:
    if isinstance(value, bool):
        raw = "yes" if value else "no"
        return PDXScalar(val=raw, raw=raw, type=SCALAR_BOOL)
    if isinstance(value, int):
        raw = str(value)
        return PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)
    if isinstance(value, float):
        raw = f"{value:g}"
        return PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)
    if isinstance(value, str):
        if re.match(r"^(rgb|hsv)\s*\{", value, re.IGNORECASE):
            return PDXScalar(val=value, raw=value, type=SCALAR_COLOR)
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return PDXScalar(val=value, raw=f'"{escaped}"', type=SCALAR_STR)
    return PDXScalar(val=str(value), raw=str(value), type=SCALAR_ID)


def _from_dict(data: Any) -> PDXBlock:
    block = PDXBlock()
    if isinstance(data, dict):
        for key, value in data.items():
            real_key = _DUP_RE.sub("", key)
            if real_key == "_anonymous_block" and isinstance(value, (dict, list)):
                block.entries.append(PDXEntry(val=_from_dict(value)))
            elif isinstance(value, (dict, list)):
                block.entries.append(PDXEntry(key=PDXScalar.id(real_key), op="=", val=_from_dict(value)))
            elif value is None:
                match = _CMP_RE.match(real_key)
                if match:
                    block.entries.append(PDXEntry(key=PDXScalar.id(match.group(1)), op=match.group(2), val=PDXScalar.id(match.group(3))))
                else:
                    block.entries.append(PDXEntry(key=PDXScalar.id(real_key)))
            else:
                block.entries.append(PDXEntry(key=PDXScalar.id(real_key), op="=", val=_make_dict_value(value)))
    elif isinstance(data, (list, tuple)):
        for item in data:
            if isinstance(item, (dict, list)):
                block.entries.append(PDXEntry(val=_from_dict(item)))
            elif isinstance(item, bool):
                raw = "yes" if item else "no"
                block.entries.append(PDXEntry(key=PDXScalar(val=raw, raw=raw, type=SCALAR_BOOL)))
            elif isinstance(item, int):
                raw = str(item)
                block.entries.append(PDXEntry(key=PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)))
            elif isinstance(item, float):
                raw = f"{item:g}"
                block.entries.append(PDXEntry(key=PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)))
            else:
                block.entries.append(PDXEntry(key=PDXScalar.id(str(item))))
    return block


def _emit_entry_tokens(entry: PDXEntry, tokens: list[Any], comments: bool = True) -> None:
    from .token import Token, TokenType

    scalar_tokens = {
        SCALAR_ID: TokenType.IDENTIFIER,
        SCALAR_NUM: TokenType.NUMBER,
        SCALAR_STR: TokenType.STRING,
        SCALAR_BOOL: TokenType.BOOLEAN,
        SCALAR_VAR: TokenType.VARIABLE,
    }
    op_tokens = {
        "=": TokenType.EQUALS,
        "!=": TokenType.NOT_EQUALS,
        "<": TokenType.LT,
        ">": TokenType.GT,
        "<=": TokenType.LE,
        ">=": TokenType.GE,
    }
    if comments:
        tokens.extend(Token(TokenType.COMMENT, comment) for comment in entry.comments)
    if entry.key:
        tokens.append(Token(scalar_tokens.get(entry.key.type, TokenType.IDENTIFIER), entry.key.val))
    if entry.op:
        tokens.append(Token(op_tokens.get(entry.op, TokenType.EQUALS), entry.op))
    if isinstance(entry.val, PDXScalar):
        if entry.val.type == SCALAR_COLOR:
            parts = str(entry.val.val).split()
            if len(parts) >= 4 and parts[1] == "{" and parts[-1] == "}":
                tokens.append(Token(TokenType.IDENTIFIER, parts[0]))
                tokens.append(Token(TokenType.LBRACE, "{"))
                tokens.extend(Token(TokenType.NUMBER, part) for part in parts[2:-1])
                tokens.append(Token(TokenType.RBRACE, "}"))
            else:
                tokens.append(Token(TokenType.IDENTIFIER, entry.val.val))
        else:
            tokens.append(Token(scalar_tokens.get(entry.val.type, TokenType.IDENTIFIER), entry.val.val))
    elif isinstance(entry.val, PDXBlock):
        tokens.append(Token(TokenType.LBRACE, "{"))
        _emit_tokens(entry.val, tokens, comments=comments)
        tokens.append(Token(TokenType.RBRACE, "}"))
    if comments and entry.inline_comment:
        tokens.append(Token(TokenType.COMMENT, entry.inline_comment))


def _emit_tokens(block: PDXBlock, tokens: list[Any], comments: bool = True) -> None:
    from .token import Token, TokenType

    for entry in block.entries:
        _emit_entry_tokens(entry, tokens, comments=comments)
    if comments:
        tokens.extend(Token(TokenType.COMMENT, comment) for comment in block.trailing_comments)
