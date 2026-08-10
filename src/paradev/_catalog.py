"""Shared catalog-query policy for user-facing adapters."""

from __future__ import annotations

from collections.abc import Mapping

CATALOG_QUERY_DEFAULT_LIMIT = 100
CATALOG_QUERY_MAX_LIMIT = 200
CATALOG_QUERY_DEFAULT_OFFSET = 0
CATALOG_QUERY_DEFAULT_INCLUDE_DATA = False
CATALOG_QUERY_MAX_HYDRATED_LIMIT = 1


def normalize_catalog_query_filters(filters: Mapping[str, object]) -> dict[str, object]:
    """Return validated finite catalog-query filters for interface adapters."""

    normalized = dict(filters)
    limit = normalized.get("limit", CATALOG_QUERY_DEFAULT_LIMIT)
    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError as error:
            raise ValueError(f"Catalog query limit must be an integer from 1 to {CATALOG_QUERY_MAX_LIMIT}.") from error
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= CATALOG_QUERY_MAX_LIMIT:
        raise ValueError(f"Catalog query limit must be an integer from 1 to {CATALOG_QUERY_MAX_LIMIT}.")

    offset = normalized.get("offset", CATALOG_QUERY_DEFAULT_OFFSET)
    if isinstance(offset, str):
        try:
            offset = int(offset)
        except ValueError as error:
            raise ValueError("Catalog query offset must be a non-negative integer.") from error
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("Catalog query offset must be a non-negative integer.")

    include_data = normalized.get("include_data", CATALOG_QUERY_DEFAULT_INCLUDE_DATA)
    if isinstance(include_data, str):
        value = include_data.strip().lower()
        if value not in {"false", "true"}:
            raise ValueError("Catalog query include_data must be true or false.")
        include_data = value == "true"
    if not isinstance(include_data, bool):
        raise ValueError("Catalog query include_data must be a boolean.")
    if include_data and limit > CATALOG_QUERY_MAX_HYDRATED_LIMIT:
        raise ValueError(f"Catalog query hydrated requests must use limit {CATALOG_QUERY_MAX_HYDRATED_LIMIT}.")

    normalized.update(limit=limit, offset=offset, include_data=include_data)
    return normalized
