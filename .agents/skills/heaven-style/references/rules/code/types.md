---
id: types
title: Type annotations
enabled: true
blocking: true
order: 25
category: code-quality
keywords: [Dict, List, Optional, Union, pipe types, builtins, TypedDict, Self]
description: Use when adding or reviewing type annotations, public signatures, Python-version compatibility, or schema-shaped data.
---

# Type annotations

## Core rule

Use current Python annotation style for new code unless the target repo pins an older runtime.

## Apply when

- Code adds or changes public function, method, class, or dataclass signatures.
- Code uses `typing.Dict`, `List`, `Tuple`, `Set`, `Optional`, `Union`, `Self`, `TypedDict`, or `Any`.
- Code returns schema-shaped dictionaries or integration-boundary payloads.

## Do

- Annotate public parameters and returns.
- Prefer built-in collection generics: `list`, `dict`, `tuple`, and `set`.
- Use `| None` on Python 3.10+.
- Use `TypedDict`, dataclasses, Pydantic models, or project `*Spec` objects when the shape matters.
- Use `Any` only at real integration boundaries.

## Avoid

- `Dict`, `List`, `Tuple`, and `Set` for Python 3.9+ code.
- Weak `dict[str, Any]` types for important internal schemas.
- Compatibility annotations unless the target repo requires them.

## Example

```python
from typing import Dict, List, Optional

def rows_by_id(rows: List[Dict[str, str]], name: Optional[str] = None) -> Dict[str, str]:
    ...
```

```python
def rows_by_id(rows: list[dict[str, str]], name: str | None = None) -> dict[str, str]:
    ...
```

## Python 3.9 compatibility

Temporarily keep `Union[...]` instead of `|` when the target project must support Python 3.9:

```python
from typing import Union

def label(value: Union[str, None]) -> str:
    ...
```

Still prefer built-in collections (`dict`, `list`, `tuple`, `set`) over `Dict`, `List`, `Tuple`, and `Set` in Python 3.9+.

## Rules

- Public functions and classes need parameter and return annotations.
- Prefer `Any` only at integration boundaries.
- Use `Self` when the supported Python version provides it; otherwise quote the class name.
- Do not add annotations that hide schema weakness. If the shape matters, define a `TypedDict`, dataclass, Pydantic model, or project `*Spec`.

## Related rules

Also apply [model.md](model.md) for public data surfaces, [oop.md](oop.md) for method contracts, and [config.md](config.md) for sentinel/default patterns.
