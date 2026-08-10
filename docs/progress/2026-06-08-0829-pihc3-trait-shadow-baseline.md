# PIHC3 Trait Shadow Baseline

Date: 2026-06-08

## Scope

Recorded the copy-root shadow baseline after importing PIHC2 country-leader traits into native PIHC3 modules.

## Result

- `paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` reports 1,581 total shadowed artifacts.
- Existing native ideas account for 1,164 warnings.
- Native traits account for 417 warnings across 139 modules.
- Each trait shadows one `common/country_leader/TRAIT_<TAG>.txt` file and two localization files.
- The warnings are non-blocking and identify the next parity-review queue before narrowing the PIHC_dev copy overlay.

## Verification

```bash
rtk uv run python - <<'PY'
import json
import subprocess

payload = json.loads(subprocess.check_output([
    "uv",
    "run",
    "paradev",
    "diagnostics",
    "projects/PIHC3",
    "--code",
    "copy_root.shadowed_artifact",
    "--json",
], text=True))
print(len(payload["diagnostics"]))
PY
```

Result: 1,581 shadowed artifacts.

Additional checks:

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py
rtk uv run paradev summary projects/PIHC3 --json
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
```

Results:

- `tests/test_sdk_examples.py`: 7 passed.
- Flake: 2 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 summary/build: `module_count: 529`, `artifact_count: 26976`, `diagnostic_count: 1581`, `error_count: 0`, `blocked: false`.
