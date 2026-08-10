# Project API Service Boundary

Status: implemented and verified

Date: 2026-08-10

## Outcome

Desktop project authoring no longer imports the REST surface. Transport-neutral
source reads, guarded draft application, single/batch module creation, guided
source forms, and localization planning now live in
`paradev.api.projects`. Both the Python desktop backend and FastAPI adapter call
those same service objects before the service delegates to `sdk.project`.

The dependency direction is now:

```text
desktop/backend ─┐
                 ├─> api/projects -> sdk/project
surfaces/rest ───┘
```

`paradev.api` remains source compatible. Its project helpers are eager,
transport-neutral aliases; `build_app` and `get_openapi_seed` resolve lazily so
importing `paradev.api.projects` or `paradev.desktop.backend` cannot initialize
REST. The wheel includes `paradev/api/__init__.pyi`, which makes those finite
lazy exports visible to type-aware clients. The generated REST facade API table
and existing import paths retain their exact 13-symbol compatibility contract.

## Verification

- Fresh-process probes prove that `paradev.api.projects` and
  `paradev.desktop.backend` do not load `paradev.surfaces.rest`.
- Desktop-then-REST and REST-then-desktop imports both pass.
- REST and public-package compatibility names are identical to the
  `api.projects` callable objects.
- The focused REST/Desktop/API/source-form/Tauri gate passed 363 tests.
- Targeted Black and Flake8 passed. The Heaven-style scanner passed all six
  production files with no banned imports.
- The wheel build passed TypeScript checking, the production Vite build, exact
  22-file frontend inventory, exact three-file host inventory, and packaged the
  new service, request validation, and typing files.

## Exact artifacts and evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel bytes: `1,823,705`
- Wheel SHA-256:
  `226151d6d1bef8c31df426aff39537a82f177ef89bc0bb3ff85f9f2b566bb662`
- Installed-App evidence:
  `dist/evidence/2026-08-10-project-api-service-app-smoke.json`
- Installed-App evidence SHA-256:
  `e2214a6c7f414186581e36cf629b1200777c18f397558170839823394859562c`
- Four-mode PIHC3 evidence:
  `dist/evidence/2026-08-10-project-api-service-four-mode-wheel-smoke.json`
- Four-mode evidence SHA-256:
  `2d31734af9809af82be67e42e9cf80d362cf0d3be74bd2db2adfeba39d13afe3`

The installed-App smoke used an isolated Python 3.12 runtime and Home, verified
the ad-hoc signature, loaded the packaged frontend, selected dynamic port
59856, terminated both app and child, and proved the unrelated listener on
4817 survived.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 83.765 | 14,573 | 106 | 33,437 |
| Cached whole project | 33.294 | 14,573 | 106 | 33,437 |
| MIO family partial | 21.700 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 21.211 | 1 | 0 | 9,298 |

Every build completed with zero diagnostics and errors. Every mode preserved
the exact clean baseline of 33,436 game files, 1,215,728,316 bytes, and SHA-256
`6793927141002c51ff39f04ee9c68df0607058bb7c2009d77104581abbad7f14`.
The installed runtime used HeavenBase 0.1.2.2, FastMCP 4.0.0b2, and MCP 2.0.0
without a developer path or app-visible `uv`.

## Scope

This slice deliberately leaves the large FastAPI route module intact; splitting
route groups is lower-priority refactor work and is not required to preserve
the corrected dependency direction. Tauri remains an optional compatibility
host. Windows integration, signing/notarization, and macOS game launch remain
deferred under the user's current priorities.
