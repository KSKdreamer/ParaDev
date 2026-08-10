"""Transport-neutral validation helpers for project API requests."""

from __future__ import annotations

from collections.abc import Mapping


def bool_value(value: object, name: str) -> bool:
    """Return one required boolean request value."""

    if not isinstance(value, bool):
        raise ValueError(f"Request field {name!r} must be a boolean.")
    return value


def module_create_batch_requests(value: object) -> list[dict[str, object]]:
    """Return a validated non-empty module-create request list."""

    if not isinstance(value, list):
        raise ValueError("Request field 'modules' must be a JSON array.")
    if not value:
        raise ValueError("Request field 'modules' must contain at least one module request.")
    modules: list[dict[str, object]] = []
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            raise ValueError(f"Request field 'modules[{index}]' must be a JSON object.")
        modules.append(dict(row))
    return modules


def optional_string(value: object, name: str) -> str | None:
    """Return one optional non-empty request string."""

    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Request field {name!r} must be a non-empty string when provided.")
    return value.strip()


def request_text(request: Mapping[str, object], *names: str) -> str:
    """Return the first present required string from equivalent field names."""

    for name in names:
        if name in request:
            return required_string(request.get(name), name)
    raise ValueError(f"Request field {names[0]!r} must be a non-empty string.")


def required_string(value: object, name: str) -> str:
    """Return one required non-empty request string."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Request field {name!r} must be a non-empty string.")
    return value.strip()


def scalar_values(value: object) -> dict[str, object]:
    """Return validated scalar template values."""

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("Request field 'values' must be an object when provided.")
    values: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Request field 'values' must use non-empty string keys.")
        if not isinstance(item, (str, int, float, bool)):
            raise ValueError(f"Request field 'values.{key}' must be a scalar value.")
        values[key.strip()] = item
    return values


def validate_request_fields(
    request: Mapping[str, object],
    allowed: frozenset[str],
    label: str,
) -> None:
    """Reject request fields outside one closed allowlist."""

    unknown = sorted(str(field) for field in request if not isinstance(field, str) or field not in allowed)
    if unknown:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(unknown)}.")
