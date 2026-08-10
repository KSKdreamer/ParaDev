# HeavenBase Catalog Query Progress

Date: 2026-06-07 05:16 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added `catalog_query(...)` to read rows from a written SQLite HeavenBase catalog without constructing a writable HeavenBase workspace.
- Added entity, name, tag, and limit filters over persisted `sys_catalog` rows.
- Added `paradev hb catalog-query <path> --json` with optional `--database`, `--entity`, `--name`, `--tag`, and `--limit` flags.
- Documented the preview, smoke, write, and query flow as the current minimal HeavenBase catalog path.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_hb.py -q` failed because `catalog_query` was missing.
- Focused green: `rtk bash scripts/test.bash tests/test_hb.py -q`
- CLI smoke: `rtk zsh -lc 'tmp="$(mktemp -d)"; cp -R demos/assets/projects/minimal "$tmp/minimal"; rtk uv run paradev hb catalog-write "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-query "$tmp/minimal" --entity pdx-symbol --json'`
- Related: `rtk bash scripts/test.bash tests/test_hb.py tests/test_cli.py tests/test_project.py tests/test_build_manifest.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py src/paradev/cli.py tests/test_hb.py`

## Review

- Query opens SQLite through `mode=ro`, so normal inspection cannot mutate the catalog database.
- The CLI accepts both `pdx-symbol` and `paradev-pdx-symbol` entity spellings, while returning the normalized Catalog target entity.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- The write path still refuses existing catalog databases; there is no refresh, replace, or undo policy yet.
- Query reads the Catalog index only. Direct typed row inspection can be added after the schema-pack shape stabilizes.
- Linear status could not be updated from this environment.

## Next

- Add an explicit catalog refresh policy so repeated writes are safe and reviewable.
- Use the persisted PDX symbol and build-artifact catalog as the bridge into the next generic compilation graph slice.
