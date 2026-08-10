"""Registry-owned presentation metadata for build families."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

FAMILY_NAVIGATION_GROUPS = frozenset(
    {"country", "military", "world", "events", "shared", "other"}
)
_FAMILY_PRESENTATION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True, slots=True)
class FamilyPresentation:
    """Stable user-facing identity and navigation placement for one family.

    This capability belongs to the registered family rather than a consuming UI.
    Project-local extensions can therefore introduce a family without changing
    ParaDev's desktop source code.
    """

    id: str
    title: str
    group: str = "other"
    aliases: tuple[str, ...] = ()
    title_key: str | None = None

    def __post_init__(self) -> None:
        """Reject ambiguous or UI-specific presentation declarations."""

        if not isinstance(self.id, str) or not _FAMILY_PRESENTATION_ID_RE.fullmatch(
            self.id
        ):
            raise ValueError(
                "Family presentation id must use lowercase kebab-case letters, "
                "digits, and hyphens."
            )
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Family presentation title must be a non-empty string.")
        if self.title != self.title.strip():
            raise ValueError(
                "Family presentation title must not have surrounding whitespace."
            )
        if self.group not in FAMILY_NAVIGATION_GROUPS:
            raise ValueError(
                "Family presentation group must be one of: "
                f"{', '.join(sorted(FAMILY_NAVIGATION_GROUPS))}."
            )
        aliases = _presentation_aliases(self.aliases)
        if aliases != self.aliases:
            raise ValueError(
                "Family presentation aliases must be a tuple of unique, normalized "
                "non-empty selectors."
            )
        if self.title_key is not None and (
            not isinstance(self.title_key, str)
            or not self.title_key.strip()
            or self.title_key != self.title_key.strip()
        ):
            raise ValueError(
                "Family presentation title_key must be a non-empty string without "
                "surrounding whitespace."
            )

    @classmethod
    def default(cls, family: str) -> FamilyPresentation:
        """Return a deterministic presentation for an undeclared external family."""

        family_id = normalize_family_selector(family)
        if not family_id:
            raise ValueError("Build family must define a presentable family id.")
        title = " ".join(part.capitalize() for part in family_id.split("-"))
        return cls(id=family_id, title=title)

    def selectors(self, family: str) -> frozenset[str]:
        """Return normalized selectors that resolve to the owning family."""

        return frozenset(
            normalize_family_selector(value)
            for value in (family, self.id, *self.aliases)
        )

    def to_view(self) -> dict[str, object]:
        """Return the JSON-safe public capability view."""

        view: dict[str, object] = {
            "id": self.id,
            "title": self.title,
            "group": self.group,
        }
        if self.aliases:
            view["aliases"] = list(self.aliases)
        if self.title_key is not None:
            view["title_key"] = self.title_key
        return view


def family_presentation_from_mapping(
    value: Mapping[str, object],
) -> FamilyPresentation:
    """Decode one strict presentation mapping."""

    unknown = set(value) - {"id", "title", "group", "aliases", "title_key"}
    if unknown:
        raise ValueError(
            f"Family presentation has unsupported fields {sorted(unknown)!r}."
        )
    family_id = value.get("id")
    title = value.get("title")
    group = value.get("group", "other")
    title_key = value.get("title_key")
    if not isinstance(family_id, str):
        raise TypeError("Family presentation id must be a string.")
    if not isinstance(title, str):
        raise TypeError("Family presentation title must be a string.")
    if not isinstance(group, str):
        raise TypeError("Family presentation group must be a string.")
    if title_key is not None and not isinstance(title_key, str):
        raise TypeError("Family presentation title_key must be a string.")
    raw_aliases = value.get("aliases", ())
    if not isinstance(raw_aliases, Sequence) or isinstance(raw_aliases, (str, bytes)):
        raise TypeError("Family presentation aliases must be a list of strings.")
    aliases: list[str] = []
    for alias in raw_aliases:
        if not isinstance(alias, str):
            raise TypeError("Family presentation aliases must be a list of strings.")
        aliases.append(alias)
    return FamilyPresentation(
        id=family_id,
        title=title,
        group=group,
        aliases=tuple(aliases),
        title_key=title_key,
    )


def normalize_family_selector(value: str) -> str:
    """Normalize a public family selector to its comparison form."""

    if not isinstance(value, str):
        return ""
    return value.strip().casefold().replace("_", "-")


def _presentation_aliases(raw: object) -> tuple[str, ...]:
    if not isinstance(raw, tuple):
        return ()
    aliases: list[str] = []
    for value in raw:
        if (
            not isinstance(value, str)
            or not value
            or value != value.strip()
            or value != value.casefold()
            or normalize_family_selector(value) != value.replace("_", "-")
        ):
            return ()
        aliases.append(value)
    if len(set(aliases)) != len(aliases):
        return ()
    return tuple(aliases)
