---
id: config
title: Config and resources
enabled: true
blocking: true
order: 20
category: code-quality
keywords: [hard-coded, magic number, literals, CM_HVNB, resources, default, model, timeout, batch size]
description: Use when code introduces defaults, tunables, prompt or resource paths, model/backend settings, or disputed literals.
---

# Config and resources

## Core rule

Tunable values live in `CM_HVNB` and package resources by default. Important user knobs stay visible in public signatures with `None` defaults, then resolve from config in the body.

## Constants versus hyperparameters

Constants are stable developer facts and may live in code: supported mode names, protocol field names, sentinel strings, fixed enum values, or mathematical identities.

Hyperparameters are values a project, deployment, benchmark, user, or caller may tune: model names, provider names, gateway routes, embedding dimensions, batch sizes, timeouts, retry counts, paths, thresholds, cache sizes, ports, and prompt text. These must come from config or resources.

Do not mention this distinction in short menus; use it when reviewing a disputed literal.

## Config ownership

Use the config manager that owns the behavior. HeavenBase is shared infrastructure, so basic utilities, logging, serialization, LLM, DB, and workspace behavior should normally route through `CM_HVNB`. App overrides should scope the owning config, for example `with CM_HVNB.scoped("my_app")`. Use a separate app config manager only for a truly separate app-specific config tree.

## Apply when

- Code adds model names, providers, gateway routes, embedding dimensions, batch sizes, timeouts, retry counts, thresholds, cache sizes, ports, paths, prompt text, SQL, or template defaults.
- Code needs package resources or package home/user-state paths.
- A literal may be either a stable protocol constant or a deployment/user-tunable value.

## Do

- Keep tunable defaults in `CM_HVNB` or package resources.
- Keep important public knobs in signatures as `None`, then resolve from config.
- Coerce config values to the needed runtime type after reading them.
- Use sentinel values when callers may intentionally pass `None`.
- Use comma-separated path parts with `CM_HVNB.pj`.

## Avoid

- Hard-coded deployable defaults in public signatures.
- Hidden important parameters that users cannot override.
- Slash-packed path strings in `pj`.
- App-specific config managers for HeavenBase-owned shared infrastructure.

## Example

```python
def embed(text: str, model: str = "deepseek-v4-flash", batch_size: int = 32) -> list[float]:
    ...
```

```python
from heavenbase.utils import CM_HVNB

def embed(
    text: str,
    model: str | None = None,
    batch_size: int | None = None,
    temperature: float | None = None,
) -> list[float]:
    model = str(model or CM_HVNB.get("heavenbase.llm.embedding.model", default="deepseek-v4-flash"))
    batch_size = int(batch_size if batch_size is not None else CM_HVNB.get("heavenbase.llm.embedding.batch_size", default=32))
    temperature = float(temperature if temperature is not None else CM_HVNB.get("heavenbase.llm.embedding.temperature", default=1.0))
    ...
```

Example config keys such as `heavenbase.llm.embedding.*` are **illustrative**. They show access patterns, not guaranteed shipped defaults. Verify keys against the target repo's config tree, bootstrap files, and tests before documenting or relying on them.

Temporarily keep `Union[...]` instead of `|` only when Python 3.9 compatibility is required by the target repo; see [types](types.md).

## Access patterns

- Use `CM_HVNB.get("dotted.key", default=...)` when a fallback is intended.
- Use positional fallback for native `dict.get`: `data.get("active", False)`. Native `dict.get` does not accept `default=`.
- Coerce types after reading config: `int(...)`, `str(...)`, `bool(...)`.
- Join paths with comma parts: `CM_HVNB.pj("cache", f"{name}.json", abs=True)`.
- Use `&` for package resources and `%` for package home/user state when the project defines those aliases.
- Store prompts, templates, SQL, and default YAML under package resources.
- For LLM, embedding, database, backend, or gateway defaults, keep provider/model/route/dimension choices in config resources and test the concrete route before documenting support.

## Path and resource example

```python
path = CM_HVNB.pj("cache/items.json")
prompt = open("src/heavenbase/resources/prompts/embed.txt").read()
```

```python
from heavenbase.utils import load_txt

path = CM_HVNB.pj("cache", "items.json", abs=True)
prompt = load_txt(CM_HVNB.pj("&", "prompts", "embed.txt"))
```

`&` means package resources. `%` means package home or user state root when the project defines it.

## Provider default example

```python
import heavenbase as hb

def embed(text: str, preset: str | None = None) -> list[float]:
    preset = preset or str(CM_HVNB.get("heavenbase.llm.embedding.preset", default="openai_embed"))
    return hb.LLM(preset=preset).embed(text)
```

## Sentinel example

```python
from typing import Union

def fetch(url: str, tag: Union[str, None, Ellipsis] = ...) -> bytes:
    if tag is ...:
        tag = CM_HVNB.get("heavenbase.http.default_tag", default=None)
    ...
```

## Related rules

Also apply [util.md](util.md) for path/file helpers, [types.md](types.md) for `Union` compatibility, [name.md](name.md) for config key naming, and [format.md](../project/format.md) for wrapper commands.
