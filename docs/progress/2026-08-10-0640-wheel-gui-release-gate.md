# Wheel GUI Release Gate

Status: completed slice

Date: 2026-08-10

## Outcome

ParaDev now has one deterministic installed-app gate for the release-critical
PIHC3 workflow. The gate creates a disposable Python environment, installs the
exact wheel, launches `paradev-gui` with an isolated home and temporary root,
verifies the packaged same-origin frontend, discovers the selected project,
and drives builds through the GUI host's public REST boundary.

The app process receives neither the developer checkout nor `uv` on `PATH`.
Runtime identity is probed from inside the isolated environment, so a green run
cannot silently import ParaDev or HeavenBase from a source checkout.

## Final artifact evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- SHA-256:
  `73787ccaa94e367a01b43a319e5ed1a964980a5660e2c5930533a59ba5ee615c`
- Evidence: `dist/python/pihc3-wheel-gui-smoke-73787cca.json`
- Installed runtime: ParaDev `0.1.0.0.dev0`, HeavenBase `0.1.2.2`,
  FastMCP `4.0.0b2`, and MCP `2.0.0`.
- Packaged frontend: same-origin bootstrap passed and a hashed JavaScript asset
  was loaded from the installed wheel.

The exact artifact completed all four required PIHC3 build modes:

| Mode | Modules | Collections | Artifacts | Diagnostics | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Clean whole project | 14,573 | 106 | 33,437 | 0 | 0 |
| Cached whole project | 14,573 | 106 | 33,437 | 0 | 0 |
| MIO family partial | 7 | 0 | 9,304 | 0 | 0 |
| `ai_bonus_weights` module partial | 1 | 0 | 9,298 | 0 | 0 |

Clean and cached whole-project summaries are exact matches. Every build was
unblocked and completed through the installed GUI host.

## Reusable release boundary

- `scripts/wheel_smoke.py` owns the portable, standard-library-only control
  plane required before dependencies have been installed.
- `scripts/smoke-wheel-gui.bash` is the repository wrapper. It supports clean,
  cached, family-partial, and module-partial build specifications plus optional
  safe project copying for small fixtures.
- `.github/workflows/release.yml` now builds wheels only through
  `scripts/build-wheel.bash`, installs the resulting artifact on Ubuntu, copies
  the minimal release fixture, and completes a cached GUI-hosted build.
- The test refuses to overwrite evidence and interrupts a live build on failure
  or timeout, keeping release diagnostics trustworthy and bounded.

## Verification

- `rtk bash scripts/test.bash`: 2,449 passed, 9 native-Windows skips.
- `rtk npm test`: 1,515 passed.
- Wheel-smoke contract tests: 13 passed.
- `rtk bash scripts/flake.bash --ci`: 234 files clean.
- `rtk npm --prefix apps/desktop run check:package`: exact 22-file GUI
  inventory passed.
- Current Heaven-style scanner: 2 standalone-control-plane files passed.
- Release workflow YAML parsing, environment/README synchronization, and
  `git diff --check`: passed.

## Remaining app work

- Cached and targeted builds still plan broadly and stage thousands of
  unchanged artifacts. The family and module counts above make this the next
  concrete performance target.
- The wheel-hosted app is reproducibly installable and build-capable, but an
  unsigned standalone `.app` wrapper is still separate work. Windows
  integration and macOS game launch remain intentionally deferred.
- Continue simplifying large-family editing and project-local extension forms
  without moving Registry-owned semantics into the frontend.
