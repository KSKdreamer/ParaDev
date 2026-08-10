"""Registry-owned module authoring capabilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ModuleIdentityContext:
    """Identity transition for one module duplication plan.

    Args:
        family (str): Registered compiler family that owns the module.
        source_object_id (str): Existing logical object identifier.
        target_object_id (str): New logical object identifier.
    """

    family: str
    source_object_id: str
    target_object_id: str


class ModuleIdentityRewriter(Protocol):
    """Extension-owned policy for creating an independent module copy."""

    identifier: str

    def rewrite_path(
        self,
        context: ModuleIdentityContext,
        relative_path: str,
    ) -> str:
        """Return the target-relative path for one source entry.

        Args:
            context (ModuleIdentityContext): Source and target module identity.
            relative_path (str): Source-relative POSIX path, or `.` for the
                module root.

        Returns:
            str: Target-relative POSIX path. The guarded copy transaction
            validates portability, ancestry, and collisions.
        """

    def rewrites_content(
        self,
        context: ModuleIdentityContext,
        relative_path: str,
    ) -> bool:
        """Return whether one regular source file contains identity text.

        Args:
            context (ModuleIdentityContext): Source and target module identity.
            relative_path (str): Source-relative POSIX file path.

        Returns:
            bool: Whether the transaction should load and rewrite the file.
        """

    def rewrite_content(
        self,
        context: ModuleIdentityContext,
        relative_path: str,
        content: bytes,
    ) -> bytes:
        """Return rewritten bytes for one declared identity-bearing file.

        Args:
            context (ModuleIdentityContext): Source and target module identity.
            relative_path (str): Source-relative POSIX file path.
            content (bytes): Exact source bytes captured by the transaction.

        Returns:
            bytes: Deterministic target bytes.

        Raises:
            UnicodeDecodeError: If a declared text source is not valid UTF-8.
        """


@dataclass(frozen=True, slots=True)
class TokenIdentityRewriter:
    """Rewrite identifier tokens in common Clausewitz text and owned paths.

    Matching treats underscores as token separators so derived identifiers
    such as `OLD_ID_DESC` and `GFX_OLD_ID` follow the new module identity,
    while alphanumeric supersets such as `OLD_ID2` remain untouched.

    Args:
        identifier (str): Stable Registry capability identifier.
        text_suffixes (tuple[str, ...]): Case-insensitive file suffixes whose
            UTF-8 content may contain the module identity.
    """

    identifier: str = "paradev.token-identity.v1"
    text_suffixes: tuple[str, ...] = (
        ".asset",
        ".csv",
        ".gfx",
        ".gui",
        ".json",
        ".loc",
        ".lua",
        ".mod",
        ".txt",
        ".yaml",
        ".yml",
    )

    def rewrite_path(
        self,
        context: ModuleIdentityContext,
        relative_path: str,
    ) -> str:
        """Return a path whose identifier tokens use the target identity.

        Args:
            context (ModuleIdentityContext): Source and target module identity.
            relative_path (str): Source-relative POSIX path, or `.`.

        Returns:
            str: Rewritten target-relative POSIX path.
        """

        if relative_path == ".":
            return relative_path
        return PurePosixPath(*(_replace_identity(part, context) for part in PurePosixPath(relative_path).parts)).as_posix()

    def rewrites_content(
        self,
        context: ModuleIdentityContext,
        relative_path: str,
    ) -> bool:
        """Return whether a file uses one of the declared text suffixes.

        Args:
            context (ModuleIdentityContext): Source and target module identity.
            relative_path (str): Source-relative POSIX file path.

        Returns:
            bool: Whether the file content should be rewritten.
        """

        del context
        return PurePosixPath(relative_path).suffix.casefold() in {suffix.casefold() for suffix in self.text_suffixes}

    def rewrite_content(
        self,
        context: ModuleIdentityContext,
        relative_path: str,
        content: bytes,
    ) -> bytes:
        """Rewrite identifier tokens in one UTF-8 source file.

        Args:
            context (ModuleIdentityContext): Source and target module identity.
            relative_path (str): Source-relative POSIX file path.
            content (bytes): Exact UTF-8 source bytes.

        Returns:
            bytes: Rewritten UTF-8 bytes.

        Raises:
            UnicodeDecodeError: If the declared text source is not valid UTF-8.
        """

        del relative_path
        return _replace_identity(content.decode("utf-8"), context).encode("utf-8")


DEFAULT_IDENTITY_REWRITER = TokenIdentityRewriter()


def _replace_identity(value: str, context: ModuleIdentityContext) -> str:
    pattern = re.compile(rf"(?<![^\W_]){re.escape(context.source_object_id)}(?![^\W_])")
    return pattern.sub(context.target_object_id, value)
