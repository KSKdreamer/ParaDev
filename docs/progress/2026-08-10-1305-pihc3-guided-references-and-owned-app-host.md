# PIHC3 Guided References And Owned App Host

Status: implemented and verified

Date: 2026-08-10

## Outcome

PIHC3 authoring now exposes Registry-owned references to existing modules and
collections without turning them into closed enums. Focus creation suggests the
28 real Focus trees for `tree`; Decision creation suggests the 62 real Decision
categories for `category_id`; users and agents may still enter a deliberate new
identifier. The same typed reference contract is shared by the ordinary editor,
batch/diagram creation, and the AI authoring catalog.

This closes the reference-discovery gap across PIHC3's 54 authoring-ready
templates and 51 visible authoring families. The existing Focus, Technology,
Doctrine, and MIO tree providers remain Registry-owned rather than frontend
family switches. The project still has 70 compiler families: 63 genuinely
project-owned Entities and seven thin compiler overlays over canonical HoI4
families.

The installed macOS app now owns its loopback server instance instead of
assuming port 4817. Finder launch requests port zero, receives one private
`paradev.gui-server-ready.v1` document containing the selected port and a
per-launch nonce, and verifies the nonce through the non-OpenAPI
`/_paradev/app-instance` endpoint before loading the WebView. Startup status and
bounded stderr use private temporary files that are unlinked immediately after
readiness, avoiding long-lived pipe callbacks in the OSA applet. Quit detaches
the app cleanly, signals only the recorded child PID, and leaves an unrelated
listener on the legacy port untouched.

The shared source-cache implementation also contains the completed topology and
loader-ABA safety closure: a stable snapshot brackets discovery, empty-directory
add/delete/rename changes invalidate the family, loader output is accepted only
for the same metadata-sensitive snapshot, and drift retries once before failing.

## Exact artifacts and evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel bytes: `1,821,415`
- Wheel SHA-256:
  `6686347f526ce06e265798608bc6e98f4895fefd455f2ae40b6c85e082b9bfce`
- Installed-App evidence:
  `dist/evidence/2026-08-10-pihc3-guided-references-app-smoke.json`
- Installed-App evidence SHA-256:
  `9f33c128907db0f74aff3ffe2cc5957fbdbe20fc845c25520f2bdc4814961f3d`
- Four-mode PIHC3 evidence:
  `dist/evidence/2026-08-10-pihc3-guided-references-four-mode-wheel-smoke.json`
- Four-mode evidence SHA-256:
  `a36c40609aba682e08d24ca9431c1c254c2ef1d9bf6135bc5d5ef7ba8e4ded0c`

The installed-App smoke used an isolated Python runtime and Home, verified the
ad-hoc signature, loaded the packaged frontend and hashed asset, selected
dynamic port 54590, terminated both app and child, and proved that the foreign
listener on 4817 survived.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 83.149 | 14,573 | 106 | 33,437 |
| Cached whole project | 31.472 | 14,573 | 106 | 33,437 |
| MIO family partial | 19.800 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 19.787 | 1 | 0 | 9,298 |

Every mode completed with zero diagnostics and errors. Each preserved the exact
clean baseline of 33,436 game files, 1,215,728,316 bytes, and SHA-256
`6793927141002c51ff39f04ee9c68df0607058bb7c2009d77104581abbad7f14`.
The hidden publication marker is validated separately.

## Verification

- Desktop gate: 93 files and 1,522 tests passed; TypeScript and the production
  Vite build passed; the packaged frontend inventory is exactly 22 files.
- Focused macOS GUI/launcher gate: 22 passed; combined source-cache and GUI gate:
  69 passed.
- Source-cache adversarial gate: 47 passed, including topology and ABA drift.
- PIHC3 template/reference tests passed, and a rendered Browser probe showed 28
  Focus-tree and 62 Decision-category suggestions while retaining free-form
  entry.
- The behavioral Python suite passed 2,697 tests with nine expected native
  Windows skips. Its sole failing assertion was generated PIHC3 bytecode
  hygiene; the disposable caches were removed and the hygiene/source-cache
  rerun passed. The final installed-wheel build matrix did not regenerate them.
- The PIHC3 retired-source guard remains clean: zero `_component`,
  `_asset_component`, `legacy`, `inactive_modules`, `.pyc`, or `__pycache__`
  source entries.
- Targeted Black/Flake8, JXA compilation, wheel inventory, shell syntax,
  `git diff --check`, and the exact installed artifact smokes passed.
- The Heaven-style scanner reports only the already documented platform-control
  and compatibility-boundary standard-library imports. Those OS integration
  seams are intentionally explicit; no new generic utility layer was added.

## Scope

Windows integration and macOS game launch remain intentionally deferred. This
checkpoint is an unsigned, usable development app rather than a signed or
notarized public release. Broad REST/desktop dependency inversion and stable
PyPI publication remain follow-up release hygiene, not blockers for PIHC3
authoring or compilation in the current app.
