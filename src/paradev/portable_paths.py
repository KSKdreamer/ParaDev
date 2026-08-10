"""Shared path identity and Windows-portability policy."""

from __future__ import annotations

import re
import unicodedata
from pathlib import PurePosixPath

_WINDOWS_INVALID_COMPONENT_CHARACTERS = frozenset('<>:"/\\|?*')
_AUTHORING_TITLE_REPLACEMENT = "－"
_CLAUSEWITZ_COLOR_CODE = re.compile(r"§.")
_CLAUSEWITZ_DYNAMIC_PARENTHETICAL = re.compile(r"\(\s*\[\?[^\]]+\][^)]*\)")
_CLAUSEWITZ_DYNAMIC_VALUE = re.compile(r"\[\?[^\]]+\]")
_CLAUSEWITZ_ICON = re.compile(r"£[^£\r\n]+£")
_CLAUSEWITZ_SUBSTITUTION = re.compile(r"\$[^$\r\n]+\$")
_WINDOWS_RESERVED_DEVICE_BASENAMES = frozenset(
    {
        "aux",
        "con",
        "conin$",
        "conout$",
        "nul",
        "prn",
        *(f"com{number}" for number in range(1, 10)),
        *(f"lpt{number}" for number in range(1, 10)),
        *(f"com{number}" for number in "¹²³"),
        *(f"lpt{number}" for number in "¹²³"),
    }
)


def portable_authoring_title(
    title: str,
    *,
    object_id: str,
    max_component_bytes: int = 255,
) -> str:
    """Return a readable filesystem-safe title suffix for one authored object.

    The localization value remains unchanged inside source files. This
    projection is only for the visible ``object_id - title`` directory name:
    Clausewitz formatting is removed, runtime substitutions are omitted,
    whitespace is collapsed, Win32-reserved characters become one readable
    full-width dash, and the suffix is truncated on a Unicode boundary.

    Args:
        title: Reader-facing localized title.
        object_id: Logical object id that prefixes the directory.
        max_component_bytes: Maximum encoded directory-component size.

    Returns:
        Portable non-empty title suffix.
    """

    if not isinstance(title, str):
        raise TypeError("Authoring title must be a string.")
    if not isinstance(object_id, str) or not object_id.strip():
        raise ValueError("Authoring object id must be a non-empty string.")
    if type(max_component_bytes) is not int or max_component_bytes <= 0:
        raise ValueError("Authoring component byte limit must be positive.")
    normalized = unicodedata.normalize("NFC", title)
    normalized = _CLAUSEWITZ_COLOR_CODE.sub("", normalized)
    normalized = _CLAUSEWITZ_DYNAMIC_PARENTHETICAL.sub("", normalized)
    normalized = _CLAUSEWITZ_DYNAMIC_VALUE.sub("", normalized)
    normalized = _CLAUSEWITZ_ICON.sub("", normalized)
    normalized = _CLAUSEWITZ_SUBSTITUTION.sub("", normalized)
    normalized = " ".join(normalized.split())
    normalized = "".join(
        _AUTHORING_TITLE_REPLACEMENT if character in _WINDOWS_INVALID_COMPONENT_CHARACTERS or ord(character) < 32 or ord(character) == 127 else character
        for character in normalized
    ).strip(" .")
    if not normalized:
        normalized = _humanized_object_id(object_id)
    prefix = f"{object_id} - "
    available = max_component_bytes - len(prefix.encode("utf-8"))
    if available <= 0:
        raise ValueError("Authoring object id leaves no room for a readable folder title.")
    normalized = _truncate_utf8(normalized, available).rstrip(" .")
    if not normalized:
        raise ValueError("Authoring folder title is empty after portable truncation.")
    return normalized


def portable_path_identity(path: str | PurePosixPath) -> str:
    """Return the NFC-and-case-folded identity used for portable collisions."""

    normalized = str(path).replace("\\", "/")
    return "/".join(unicodedata.normalize("NFC", part).casefold() for part in PurePosixPath(normalized).parts)


def windows_portable_component_error(component: str) -> str | None:
    """Return why one path component cannot be emitted portably, if applicable."""

    if not component or component in {".", ".."}:
        return "is empty or is a traversal alias"
    if component.endswith((" ", ".")):
        return "ends with a space or dot"
    if any(character in _WINDOWS_INVALID_COMPONENT_CHARACTERS or ord(character) < 32 or ord(character) == 127 for character in component):
        return "contains a Win32-reserved character or control character"
    basename = component.split(".", 1)[0].rstrip(" .").casefold()
    if basename in _WINDOWS_RESERVED_DEVICE_BASENAMES:
        return "uses a Windows-reserved device basename"
    return None


def _humanized_object_id(object_id: str) -> str:
    words = object_id.replace("-", "_").split("_")
    return " ".join(word if word.isupper() else word.capitalize() for word in words if word)


def _truncate_utf8(value: str, limit: int) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= limit:
        return value
    return encoded[:limit].decode("utf-8", errors="ignore")
