"""Paradox game package adapters."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .hoi4 import build_registry as build_hoi4_registry

if TYPE_CHECKING:
    from paradev.build import BuildRegistry

PROFILE_REGISTRIES: dict[str, Callable[[], "BuildRegistry"]] = {
    "hoi4": build_hoi4_registry,
}


def registry_for_profile(profile: str) -> "BuildRegistry":
    """Return a build registry for a named game profile.

    Args:
        profile: Game or build profile identifier.

    Returns:
        Build registry with profile default families and writers.

    Raises:
        ValueError: If no profile registry is known.
    """

    key = profile.strip().lower()
    try:
        create = PROFILE_REGISTRIES[key]
    except KeyError as error:
        raise ValueError(f"Build profile {profile!r} is not registered.") from error
    return create()


from .api import (  # noqa: E402
    GAMES_API_TABLE_SCHEMA,
    GamesApiRow,
    GamesApiTable,
    get_games_api_selection,
    get_games_api_table,
    render_games_api_reference_markdown,
)

__all__ = [
    "PROFILE_REGISTRIES",
    "registry_for_profile",
    "GAMES_API_TABLE_SCHEMA",
    "GamesApiRow",
    "GamesApiTable",
    "get_games_api_selection",
    "get_games_api_table",
    "render_games_api_reference_markdown",
]
