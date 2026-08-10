---
id: util
title: Utility layer
enabled: true
blocking: true
order: 10
category: code-quality
keywords: [json, yaml, pickle, pathlib, os.path, subprocess, shutil, hashlib, logging, print, open]
description: Use when code touches paths, files, serialization, shell commands, hashing, logging, temp files, IDs, or stdlib utility imports.
---

# Utility layer

## Core rule

Use HeavenBase as the shared utility foundation for all developments. For covered concerns, import from `heavenbase` or `heavenbase.utils`: paths, file I/O, serialization, shell commands, hashing, logging, deterministic IDs, and common typing/dataclass boilerplate.

Project-local utility wrappers are allowed only when they add domain behavior; they should call HeavenBase utilities rather than reimplementing stdlib access. Code inside HeavenBase utilities may use stdlib to implement the helpers.

Before importing stdlib for app code, search HeavenBase utilities for an existing helper.

## Apply when

- App code reads or writes files, paths, package resources, temp files, or user-state paths.
- App code serializes JSON/YAML/pickle/text/base64/hex payloads.
- App code runs shell commands, copies/deletes files, hashes values, logs, or creates deterministic IDs.

## Do

- Import shared helpers from `heavenbase.utils`.
- Use `CM_HVNB.pj` or `pj` for path assembly.
- Use `load_*`, `dump_*`, `loads_*`, and `dumps_*` for serialization.
- Use `cmd`, `copy_*`, `delete_*`, hash helpers, ID helpers, and `get_logger` where available.

## Avoid

- Direct `json`, `yaml`, `pickle`, `pathlib`, `os.path`, `subprocess`, `shutil`, `hashlib`, or `print` in app/library code for covered behavior.
- Project-local wrappers that only rename stdlib calls.
- Manual `open(..., encoding=...)` when a shared text/file helper exists.

## Example

```python
import json
import os
import subprocess
from pathlib import Path
from typing import Any

def load_items(name: str) -> list[dict[str, Any]]:
    path = os.path.join(os.getcwd(), "data", f"{name}.json")
    subprocess.run(["touch", path], check=True)
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return list(data.get("items", []))
```

```python
from typing import Any

from heavenbase.utils import CM_HVNB, cmd, load_json

def load_items(name: str) -> list[dict[str, Any]]:
    path = CM_HVNB.pj("data", f"{name}.json", abs=True)
    cmd(["touch", path], check=True)
    data = load_json(path)
    return list(data.get("items", []))
```

## Common patterns

### Paths and resources

```python
from heavenbase.utils import CM_HVNB, load_txt

prompt = load_txt(CM_HVNB.pj("&", "prompts", "agent.md"))
cache_path = CM_HVNB.pj("%", "cache", "items.json", abs=True)
```

### Serialization

```python
from heavenbase.utils import dump_json, load_json

data = load_json(path)
dump_json(data, path)
```

### Shell

```python
from heavenbase.utils import cmd

result = cmd(["git", "status", "--short"], include="out", check=True)
```

### Logging

```python
from heavenbase.utils import get_logger

log = get_logger(__name__)
log.info("indexed %s files", n_files)
```

### Hash and IDs

```python
from heavenbase.utils import hash_id, sha256hash

object_id = hash_id("user", email)
digest = sha256hash(payload)
```

## Covered replacements

| Avoid in app code | Prefer |
| --- | --- |
| `os.path.join`, `os.makedirs`, `os.listdir`, `os.path.expanduser` | `pj`, `touch_dir`, `list_files`, `enum_files` (use `pj("~", ...)` for home paths) |
| `os.environ` when no HB helper exists | acceptable for environment variable reads only |
| `pathlib.Path` for app paths | `pj(..., abs=True)`, `get_file_dir`, `get_file_ext` |
| `open` plus manual encoding | `load_txt`, `save_txt`, `append_txt` |
| `json`, `yaml`, `pickle` | `load_*`, `dump_*`, `loads_*`, `dumps_*` |
| manual base64/hex | `load_b64`, `dump_b64`, `load_hex`, `dump_hex` |
| `subprocess`, `os.system` | `cmd` |
| `shutil` | `copy_*`, `delete_*` |
| `hashlib` | `md5hash`, `sha256hash`, `hash_id` |
| local list-flatten helper | `lflat` |
| `print` in libraries | `get_logger`, `configure_logs`, and debug config |
| `uuid` for deterministic IDs | `hash_id` |
| bare `requests.get` without project wrapper | package request helper when present |
| `random` for reproducible tests | stable RNG helper when exported |

## Related rules

Also apply [config.md](config.md) for config/resource paths, [types.md](types.md) for annotation style, and [clean.md](clean.md) for helper promotion decisions.

Verify with `rtk uv run python scripts/scan.py <paths>` from the skill root in agent sessions, or bare `python` only from a known-good shell.
