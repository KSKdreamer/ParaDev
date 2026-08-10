---
id: error
title: Errors
enabled: true
blocking: true
order: 60
category: code-quality
keywords: [try except, logging, raise, print debug, raise_mismatch, unsupported value, swallowed error]
description: Use when validating supported values, handling exceptions, logging failures, catching broadly, or returning fallbacks.
---

# Errors

## Core rule

Raise with context. Catch only at defined boundaries such as CLI, HTTP handlers, workers, and integration adapters. Use project logging helpers; gate verbose output on debug config.

For unsupported choices, prefer `raise_mismatch` when the utility exists. HeavenBase's version supports stable suggestions, configurable modes (`ignore`, `match`, `warn`, `exit`, `raise`), case sensitivity, normalizers, and contextual comments.

## Apply when

- Code validates modes, providers, backend names, enum-like choices, or user input.
- Code catches exceptions, logs failures, returns fallbacks, or exits.
- Code handles decoded external payloads.

## Do

- Raise contextual exceptions at the point where invalid state is known.
- Use `raise_mismatch` for supported-value checks when available.
- Catch exceptions only at boundary layers and preserve cause/context.
- Use logging helpers instead of `print`.

## Avoid

- Bare `except:`.
- Broad `except Exception` around one-liners.
- `assert` for runtime validation.
- Swallowed errors and silent `{}`/`None` fallbacks.
- `print` in library code.

## Example

```python
def parse_job(payload: bytes, mode: str) -> dict[str, object]:
    try:
        if mode not in MODES:
            raise ValueError(f"unknown mode: {mode}")
        return loads_json(payload)
    except Exception:
        print("bad job")
        return {}
```

```python
from heavenbase.utils import loads_json, raise_mismatch

def parse_job(payload: bytes, mode: str) -> dict[str, object]:
    mode = raise_mismatch(MODES, mode, name="job mode")
    data = loads_json(payload)
    if not isinstance(data, dict):
        raise TypeError(f"job payload must decode to dict, got {type(data).__name__}")
    return data
```

## Related rules

Also apply [util.md](util.md) for logging/serialization helpers and [types.md](types.md) for decoded payload shape.
